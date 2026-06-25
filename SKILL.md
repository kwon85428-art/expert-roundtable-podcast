---
name: expert-roundtable-podcast
description: End-to-end pipeline: topic → expert roundtable discussion script → DashScope CosyVoice cloned-voice TTS → podcast MP3 + SRT subtitles. Use when the user wants a complete AI podcast with cloned scholar voices from 阿里云百炼.
---

# Expert Roundtable Podcast Pipeline

## Overview

This skill produces a complete AI podcast + presentation deck from a roundtable topic in one pipeline:

```
Topic + Experts → [energy-expert-roundtable] → Script → [DashScope CosyVoice TTS] → MP3 + SRT + PPT
```

Four stages, each can run independently or as a full pipeline.

---

## Stage 1: Script Generation

Follow the **energy-expert-roundtable** skill to produce a discussion script in Markdown format:

```markdown
**老桂**：开场白...

**戴金星**：我的判断...

**邹才能**：我补充...

**马永生**：从战略角度...
```

Rules:
- Speaker names match the voice IDs in Stage 2
- Pure spoken text, no tables or markdown formatting
- Target 5-8 minutes (~1500-2000 spoken characters)
- Format: `SpeakerName：text` (Chinese colon)
- Cross-examination uses `主持人 → ExpertName：question`

---

## Stage 2: Voice Cloning & TTS

### Prerequisites

1. 阿里云百炼 DashScope API Key ([获取](https://bailian.console.aliyun.com/))
2. Cloned voices in 百炼 console (声音克隆)
3. Python 3.9+ with `dashscope` SDK

### Setup

```bash
python3 -m venv /tmp/ds-venv
/tmp/ds-venv/bin/pip install dashscope
```

### SDK Patch (REQUIRED)

`cosyvoice-v3.5-plus` has a response format mismatch with the SDK. Patch before use:

```bash
# Patch the SDK to handle missing begin_time in cosyvoice-v3.5-plus responses
SDK_PATH=$(/tmp/ds-venv/bin/python3 -c "import dashscope; print(dashscope.__path__[0])")
python3 << 'PYEOF'
path = f"$SDK_PATH/audio/tts/speech_synthesizer.py"
with open(path) as f:
    content = f.read()

# Fix 1: Skip empty dicts without "sentence" key
old1 = '''                    else:
                        if _callback is not None:
                            sentence = SpeechSynthesisResult(
                                None,  # type: ignore[arg-type]
                                None,  # type: ignore[arg-type]
                                part.output["sentence"],'''
new1 = '''                    else:
                        if isinstance(part.output, dict) and "sentence" not in part.output:
                            continue
                        if _callback is not None:
                            sentence = SpeechSynthesisResult(
                                None,  # type: ignore[arg-type]
                                None,  # type: ignore[arg-type]
                                part.output["sentence"],'''
content = content.replace(old1, new1)

# Fix 2: Use .get() for begin_time/end_time
old2 = '''                        if len(_sentences) == 0:
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
                                _sentences.append(part.output["sentence"])'''
new2 = '''                        if len(_sentences) == 0:
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
                                _sentences.append(part.output["sentence"])'''
content = content.replace(old2, new2)

with open(path, 'w') as f:
    f.write(content)
print("SDK patched successfully")
PYEOF
```

### List Cloned Voices

```python
import os
os.environ['DASHSCOPE_API_KEY'] = 'your-key'
from dashscope.audio.tts_v2.enrollment import VoiceEnrollmentService
svc = VoiceEnrollmentService()
for v in svc.list_voices():
    print(f"{v['gmt_create']} | {v['voice_id']} | {v['target_model']}")
```

### Configure Voice Mapping

```python
VOICES = {
    "老桂": "cosyvoice-v3.5-plus-bailian-xxxx",
    "戴金星": "cosyvoice-v3.5-plus-bailian-xxxx",
    "邹才能": "cosyvoice-v3.5-plus-bailian-xxxx",
    "马永生": "cosyvoice-v3.5-plus-bailian-xxxx",
}
MODEL = "cosyvoice-v3.5-plus"  # or cosyvoice-v3.5-flash
```

### Generate TTS Segments

Use `batch_generate.py` to parse the script and call TTS for each speaker segment:

```bash
/tmp/ds-venv/bin/python3 batch_generate.py
# Outputs: audio_segments/0000_Speaker.wav (12-20 segments, ~12 MB total)
```

Each segment is a WAV file: 24000Hz, mono, 16-bit PCM.

---

## Stage 3: Concatenate & Generate SRT

### Concatenate with Gaps

Use `concat_podcast.py`:

```bash
python3 concat_podcast.py
# Outputs: podcast.mp3 + podcast.srt
```

Gap logic:
- Same speaker consecutive segments: 0.4s silence
- Different speaker: 0.8s silence
- First segment: no leading silence

### SRT Format

```
1
00:00:00,000 --> 00:00:24,589
老桂：开场白第一行
开场白第二行

2
00:00:25,390 --> 00:01:11,159
戴金星：发言内容...
```

---

## Stage 4: PPT 生成（可选）

根据讨论稿自动生成专业演示文稿：

```bash
npm install pptxgenjs
node make_pptx.js
# Outputs: roundtable.pptx
```

PPT 结构（~10 页）：
- 标题页（深色背景 + 主题色腰线）
- 核心数据卡片（关键数字可视化）
- 主持人开场 / 问题重述
- 每位专家评议各一页（✅共识 + ⚠️质疑）
- 共识与分歧双栏对比
- 关键交锋速览
- 核心结论 + 下一步
- 结尾页

配色方案见 `make_pptx.js` 顶部 `C` 对象，可根据话题调整。

---

## Full Pipeline Quickstart

```bash
# 1. Write script (manual or with energy-expert-roundtable)
# 2. Set API key
export DASHSCOPE_API_KEY="sk-xxx"

# 3. Setup & patch
python3 -m venv /tmp/ds-venv && /tmp/ds-venv/bin/pip install dashscope
python3 patch_sdk.py

# 4. Configure VOICES in batch_generate.py

# 5. Generate audio segments
/tmp/ds-venv/bin/python3 batch_generate.py

# 6. Concat + SRT
python3 concat_podcast.py

# 7. (Optional) Generate PPT
npm install pptxgenjs && node make_pptx.js

# Output: podcast.mp3, podcast.srt, roundtable.pptx
```

---

## Voice Models

| Model | Speed | Quality | Use Case |
|---|---|---|---|
| `cosyvoice-v3.5-plus` | ~15s per segment | Highest | Final production |
| `cosyvoice-v3.5-flash` | ~5s per segment | Good | Draft/testing |

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| `KeyError: 'sentence'` | Apply SDK patch (see Stage 2) |
| `KeyError: 'begin_time'` | Apply SDK patch (see Stage 2) |
| `current user api does not support http call` | API key is WebSocket-only — use SDK (not REST) |
| `Access denied` for qwen-tts models | Use `cosyvoice-v3.5-plus` (the cloned voice model) |
| Audio is raw data, not playable | Pass `format='wav'` to `SpeechSynthesizer.call()` |
| Different segment durations for same text | TTS varies slightly per call — SRT accounts for actual durations |
