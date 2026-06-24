#!/usr/bin/env python3
"""
Batch TTS generation for expert roundtable podcast.
Parses a script (Markdown, Speaker：text format) and generates WAV segments
via DashScope CosyVoice cloned-voice API.

Usage:
    1. Set DASHSCOPE_API_KEY env var or edit API_KEY below
    2. Configure VOICES dict with speaker → voice_id mapping
    3. Set SCRIPT_PATH to your script file
    4. Run: python3 batch_generate.py
"""

import os
import re
import json
import sys
import time

# ========== CONFIGURATION ==========

API_KEY = os.environ.get("DASHSCOPE_API_KEY", "sk-your-key-here")

# Voice mapping: script speaker name → DashScope cloned voice ID
VOICES = {
    "老桂": "cosyvoice-v3.5-plus-bailian-xxxx",
    "戴金星": "cosyvoice-v3.5-plus-bailian-xxxx",
    "邹才能": "cosyvoice-v3.5-plus-bailian-xxxx",
    "马永生": "cosyvoice-v3.5-plus-bailian-xxxx",
}

MODEL = "cosyvoice-v3.5-plus"  # or cosyvoice-v3.5-flash
SCRIPT_PATH = "script.md"      # path to roundtable script
OUTDIR = "audio_segments"      # output directory for WAV files

# ====================================

os.environ["DASHSCOPE_API_KEY"] = API_KEY


def parse_script(path):
    """Parse Markdown script into (speaker, text) segments.

    Recognized format:
        SpeakerName：text on same line
        Continuation lines without speaker prefix

    Headers (#), tables (|), and blank lines are skipped.
    "主持人 → Expert" arrow notation is resolved to the moderator.
    """
    segments = []
    with open(path) as f:
        lines = f.readlines()

    current_speaker = None
    current_lines = []

    for line in lines:
        line = line.rstrip()
        if not line or line.startswith("#") or line.startswith("|"):
            continue

        match = re.match(r"^(.+?)[：:]\s*(.*)", line)
        if match:
            raw_speaker = match.group(1).strip()
            text = match.group(2).strip()

            # Resolve arrow notation: "老桂 → 戴金星" → "老桂"
            if "→" in raw_speaker:
                raw_speaker = raw_speaker.split("→")[0].strip()

            if raw_speaker in VOICES:
                if current_speaker and current_lines:
                    segments.append((current_speaker, " ".join(current_lines)))
                current_speaker = raw_speaker
                current_lines = [text] if text else []
            elif current_speaker:
                current_lines.append(line)
        else:
            if current_speaker:
                current_lines.append(line)

    if current_speaker and current_lines:
        segments.append((current_speaker, " ".join(current_lines)))

    return segments


def generate_tts(speaker, text, index, outdir):
    """Generate one TTS segment. Returns (filename, size_bytes) or (None, 0)."""
    from dashscope.audio.tts import SpeechSynthesizer

    vid = VOICES[speaker]
    print(f"[{index:03d}] {speaker}: {text[:60]}...")

    for attempt in range(3):
        try:
            result = SpeechSynthesizer.call(
                model=MODEL,
                text=text,
                voice=vid,
                format="wav",  # WAV header for proper ffmpeg handling
            )
            audio = result.get_audio_data()
            if audio:
                filename = f"{index:04d}_{speaker}.wav"
                filepath = os.path.join(outdir, filename)
                with open(filepath, "wb") as f:
                    f.write(audio)
                print(f"  ✅ {len(audio):,} bytes → {filepath}")
                return filename, len(audio)
            else:
                print(f"  ⚠️  no audio data, retry {attempt + 1}/3")
        except Exception as e:
            print(f"  ❌ {e}, retry {attempt + 1}/3")
            time.sleep(2)

    print(f"  ❌ FAILED after 3 attempts")
    return None, 0


def main():
    os.makedirs(OUTDIR, exist_ok=True)

    print("=== Parsing script ===")
    segments = parse_script(SCRIPT_PATH)
    print(f"Found {len(segments)} segments\n")
    for i, (spk, txt) in enumerate(segments):
        print(f"  [{i:03d}] {spk}: {txt[:80]}...")

    print("\n=== Generating TTS ===")
    manifest = []
    for i, (speaker, text) in enumerate(segments):
        fname, size = generate_tts(speaker, text, i, OUTDIR)
        manifest.append(
            {
                "index": i,
                "speaker": speaker,
                "file": fname,
                "size": size,
                "text_preview": text[:80],
            }
        )

    manifest_path = os.path.join(OUTDIR, "manifest.json")
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    success = sum(1 for m in manifest if m["file"])
    print(f"\n=== Done: {success}/{len(manifest)} segments ===")
    print(f"Manifest: {manifest_path}")
    print(f"Next: run concat_podcast.py")


if __name__ == "__main__":
    main()
