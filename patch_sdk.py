#!/usr/bin/env python3
"""
Patch the DashScope SDK for cosyvoice-v3.5-plus compatibility.

The v3.5-plus model returns sentence objects without begin_time/end_time,
and sends empty dicts. This patches dashscope.audio.tts.speech_synthesizer
to handle both.

Usage:
    python3 patch_sdk.py
"""

import os
import sys


def patch_sdk():
    """Apply compatibility patches to the installed dashscope SDK."""
    try:
        import dashscope
    except ImportError:
        print("❌ dashscope not installed. Run: pip install dashscope")
        sys.exit(1)

    sdk_dir = dashscope.__path__[0]
    target = os.path.join(sdk_dir, "audio", "tts", "speech_synthesizer.py")

    if not os.path.exists(target):
        print(f"❌ Cannot find speech_synthesizer.py at {target}")
        sys.exit(1)

    with open(target) as f:
        content = f.read()

    # Fix 1: Skip responses without "sentence" key (empty dicts)
    old1 = """                    else:
                        if _callback is not None:
                            sentence = SpeechSynthesisResult(
                                None,  # type: ignore[arg-type]
                                None,  # type: ignore[arg-type]
                                part.output["sentence"],"""

    new1 = """                    else:
                        if isinstance(part.output, dict) and "sentence" not in part.output:
                            continue
                        if _callback is not None:
                            sentence = SpeechSynthesisResult(
                                None,  # type: ignore[arg-type]
                                None,  # type: ignore[arg-type]
                                part.output["sentence"],"""

    if old1 not in content:
        print("⚠️  Fix 1 already applied or SDK version changed")
    else:
        content = content.replace(old1, new1)
        print("✅ Fix 1 applied: skip empty dicts")

    # Fix 2: Use .get() for begin_time/end_time
    old2 = """                        if len(_sentences) == 0:
                            _sentences.append(part.output["sentence"])
                        else:
                            if (
                                _sentences[-1]["begin_time"]
                                == part.output["sentence"]["begin_time"]
                            ):
                                if (
                                    _sentences[-1]["end_time"]
                                    != part.output["sentence"]["end_time"]
                                ):
                                    _sentences.pop()
                                    _sentences.append(part.output["sentence"])
                            else:
                                _sentences.append(part.output["sentence"])"""

    new2 = """                        if len(_sentences) == 0:
                            _sentences.append(part.output["sentence"])
                        else:
                            prev_begin = _sentences[-1].get("begin_time")
                            curr_begin = part.output["sentence"].get("begin_time")
                            if prev_begin is not None and curr_begin is not None and prev_begin == curr_begin:
                                if (
                                    _sentences[-1].get("end_time")
                                    != part.output["sentence"].get("end_time")
                                ):
                                    _sentences.pop()
                                    _sentences.append(part.output["sentence"])
                            else:
                                _sentences.append(part.output["sentence"])"""

    if old2 not in content:
        print("⚠️  Fix 2 already applied or SDK version changed")
    else:
        content = content.replace(old2, new2)
        print("✅ Fix 2 applied: .get() for begin_time/end_time")

    with open(target, "w") as f:
        f.write(content)

    print(f"\n🎉 SDK patched at: {target}")


if __name__ == "__main__":
    patch_sdk()
