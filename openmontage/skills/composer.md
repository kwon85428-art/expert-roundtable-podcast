# Composer - Expert Roundtable to Video

## Input

- `scene_plan.json` — timed scenes with speaker assignments
- `asset_manifest.json` — paths to speaker cards and background images
- `podcast.mp3` — audio track
- `podcast.srt` — subtitles

## Output

- `roundtable-video.mp4` — final rendered video
- `render_report.json` — validation results

## Process

### 1. Build Remotion Composition

Create a Remotion project with these components:

```jsx
// Scene component per subtitle segment
<Scene speaker={speaker} text={text} background={bgImage}>
  <SpeakerCard name={speaker} image={cardImage} />
  <Subtitles text={text} timing={timing} />
  <Background src={bgImage} />
</Scene>
```

### 2. Layout

```
┌──────────────────────────────────────────┐
│  [Background image or gradient]          │
│                                          │
│  ┌────────────────────────────────────┐  │
│  │ 👤 戴金星 · 中国科学院院士        │  │ ← Speaker card (top, semi-transparent)
│  └────────────────────────────────────┘  │
│                                          │
│        扩散动力学的定量约束              │
│      确实是我们这个领域长期             │  ← Word-level subtitles (center)
│         忽略的问题                       │
│                                          │
└──────────────────────────────────────────┘
```

### 3. Animation

- Speaker card: slide in from left, 0.3s ease-out
- Subtitles: word-by-word highlight with karaoke effect
- Background: subtle Ken Burns zoom (1.02 → 1.05 over segment duration)
- Scene transitions: crossfade 0.3s between speaker changes

### 4. Render

```bash
cd remotion-composer
npx remotion render RoundtableVideo out/roundtable-video.mp4 \
  --props='{"scenePlan": "scene_plan.json", "audio": "podcast.mp3", "srt": "podcast.srt"}'
```

### 5. Validate

```bash
ffprobe -v error -show_entries format=duration,size roundtable-video.mp4
```

Passes if:
- Duration matches podcast (±0.5s)
- Resolution: 1920×1080
- Has audio stream
- File size > 1 MB
