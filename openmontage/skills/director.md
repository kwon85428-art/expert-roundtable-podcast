# Director - Expert Roundtable to Video Pipeline

## When To Use

You have a complete roundtable podcast package (script.md + podcast.mp3 + podcast.srt)
from the expert-roundtable-podcast skill. Convert it into a video with speaker cards,
animated subtitles, and background visuals.

## Prerequisites

Before starting, verify these files exist in the working directory:

| File | Required | Source |
|------|----------|--------|
| `podcast.mp3` | ✅ | Stage 3 output |
| `podcast.srt` | ✅ | Stage 3 output |
| `script.md` | ✅ | Stage 1 output |

## Process

### 1. Identify the project

The script.md metadata block tells you:
- Topic (line starting with `主题：`)
- Moderator (`主持人：`)
- Expert list (`专家：`)

### 2. Route to the pipeline

Run through the three stages sequentially:
1. **scene_plan** — parse SRT + script into timed scenes
2. **assets** — generate speaker cards and validate subtitles
3. **compose** — build Remotion composition and render to MP4

### 3. Speaker Card Design

Generate a simple speaker card for each unique speaker:
- Background: dark gradient (matching roundtable theme)
- Speaker name in large white text
- Brief title/affiliation below
- 1920×200 px, PNG format

Use `image_gen` with FLUX or fall back to programmatic generation with Pillow.

### 4. Visual Background

Per speaker or per segment, use one of:
- **Free stock** (Pexels/Unsplash) — search for abstract/science/geology images
- **Solid color background** with subtle gradient — cheapest, always works
- **AI-generated** (FLUX via fal.ai) — best quality, ~$0.01/image

### 5. Budget

Default $0.50 cap. At zero API keys:
- Piper TTS → skip (audio already exists)
- Pillow speaker cards → free
- Free stock backgrounds → free  
- Remotion composition → free
- FFmpeg render → free

**Total: $0.00 with zero keys.**
