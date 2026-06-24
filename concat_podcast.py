#!/usr/bin/env python3
"""
Concatenate TTS segments into a podcast MP3 and generate SRT subtitles.

Usage:
    Run after batch_generate.py. Reads audio_segments/manifest.json
    and audio_segments/*.wav, outputs podcast.mp3 + podcast.srt.

Requirements:
    ffmpeg, ffprobe (install: brew install ffmpeg)
"""

import json
import os
import re
import subprocess

# ========== CONFIGURATION ==========

SEGMENTS_DIR = "audio_segments"
MANIFEST_FILE = os.path.join(SEGMENTS_DIR, "manifest.json")
SCRIPT_PATH = "script.md"
OUTPUT_MP3 = "podcast.mp3"
OUTPUT_SRT = "podcast.srt"

# Gap between segments (seconds)
GAP_SAME_SPEAKER = 0.4   # same speaker, consecutive segments
GAP_DIFF_SPEAKER = 0.8   # different speakers

# ====================================


def get_full_texts(script_path, speakers):
    """Re-parse script to get full texts (manifest has previews only)."""
    with open(script_path) as f:
        lines = f.readlines()

    segs = []
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
            if "→" in raw_speaker:
                raw_speaker = raw_speaker.split("→")[0].strip()
            if raw_speaker in speakers:
                if current_speaker and current_lines:
                    segs.append(" ".join(current_lines))
                current_speaker = raw_speaker
                current_lines = [text] if text else []
            elif current_speaker:
                current_lines.append(line)
        else:
            if current_speaker:
                current_lines.append(line)

    if current_speaker and current_lines:
        segs.append(" ".join(current_lines))

    return segs


def format_srt_time(seconds):
    """Convert float seconds to SRT timestamp: HH:MM:SS,mmm"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    millis = int((secs - int(secs)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{int(secs):02d},{millis:03d}"


def main():
    # Load manifest
    with open(MANIFEST_FILE) as f:
        segments = json.load(f)

    # Get speakers set
    speakers = set(s["speaker"] for s in segments)

    # Get full texts
    full_texts = get_full_texts(SCRIPT_PATH, speakers)

    if len(full_texts) != len(segments):
        print(f"⚠️  Text count ({len(full_texts)}) ≠ segment count ({len(segments)})")

    # === Step 1: Pad each segment with silence at the end ===
    print("=== Padding segments with silence gaps ===")
    prev_speaker = None

    for i, seg in enumerate(segments):
        infile = os.path.join(SEGMENTS_DIR, seg["file"])
        outfile = os.path.join(SEGMENTS_DIR, f"padded_{i:04d}.wav")

        # Compute gap: silence BEFORE this segment (gap after previous)
        if i == 0:
            gap = 0  # no gap before first segment
        else:
            gap = GAP_SAME_SPEAKER if seg["speaker"] == prev_speaker else GAP_DIFF_SPEAKER

        # Add silence at the END of previous segment = gap before current
        # Actually, pad current segment at the BEGINNING
        # But apad only pads at end. Use adelay to delay.
        if gap > 0:
            delay_ms = int(gap * 1000)
            cmd = [
                "ffmpeg", "-y", "-i", infile,
                "-af", f"adelay={delay_ms}|{delay_ms}",
                outfile,
            ]
        else:
            cmd = ["ffmpeg", "-y", "-i", infile, outfile]

        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            print(f"  ❌ pad [{i}]: {r.stderr[-200:]}")
        else:
            print(f"  [{i:02d}] +{gap:.1f}s gap → {outfile}")

        prev_speaker = seg["speaker"]

    # === Step 2: Get durations for SRT ===
    print("\n=== Computing durations ===")
    timings = []
    cumulative = 0.0

    for i, seg in enumerate(segments):
        wav_file = os.path.join(SEGMENTS_DIR, seg["file"])
        r = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "csv=p=0", wav_file],
            capture_output=True, text=True,
        )
        seg_dur = float(r.stdout.strip())

        # Gap before this segment
        if i == 0:
            gap = 0
        else:
            gap = GAP_SAME_SPEAKER if seg["speaker"] == timings[-1]["speaker"] else GAP_DIFF_SPEAKER

        cumulative += gap
        start_time = cumulative
        end_time = cumulative + seg_dur
        cumulative = end_time

        text = full_texts[i] if i < len(full_texts) else seg.get("text_preview", "")
        timings.append({
            "index": i,
            "speaker": seg["speaker"],
            "start": start_time,
            "end": end_time,
            "text": text,
            "gap": gap,
        })

    # === Step 3: Concatenate padded WAVs to MP3 ===
    print("\n=== Concatenating to MP3 ===")

    concat_file = os.path.join(SEGMENTS_DIR, "concat.txt")
    with open(concat_file, "w") as f:
        for i in range(len(segments)):
            f.write(f"file 'padded_{i:04d}.wav'\n")

    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0",
         "-i", concat_file,
         "-acodec", "libmp3lame", "-ab", "128k",
         "-ar", "44100", "-ac", "1",
         OUTPUT_MP3],
        cwd=SEGMENTS_DIR,
        capture_output=True,
    )

    # Verify
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", OUTPUT_MP3],
        capture_output=True, text=True,
    )
    total_dur = float(r.stdout.strip())
    print(f"  {OUTPUT_MP3}: {total_dur:.1f}s = {total_dur / 60:.1f} min")

    # === Step 4: Generate SRT ===
    print("\n=== Generating SRT ===")

    srt_lines = []
    for i, t in enumerate(timings):
        full = t["text"]
        # Split long text at ~40 char boundary
        if len(full) > 50:
            mid = len(full) // 2
            for j in range(mid, max(mid - 20, 0), -1):
                if full[j] in "。！？，、；：":
                    mid = j + 1
                    break
            subtitle_text = f"{full[:mid]}\n{full[mid:]}"
        else:
            subtitle_text = full

        srt_lines.append(str(i + 1))
        srt_lines.append(
            f"{format_srt_time(t['start'])} --> {format_srt_time(t['end'])}"
        )
        srt_lines.append(subtitle_text)
        srt_lines.append("")

    with open(OUTPUT_SRT, "w") as f:
        f.write("\n".join(srt_lines))
    print(f"  {OUTPUT_SRT}: {len(timings)} entries")

    # === Summary ===
    print(f"\n{'='*50}")
    print(f"✅ Done!")
    print(f"   Audio: {OUTPUT_MP3}  ({total_dur:.0f}s = {total_dur/60:.1f} min)")
    print(f"   Subs:  {OUTPUT_SRT}  ({len(timings)} entries)")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
