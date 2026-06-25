# Scene Planner - Expert Roundtable to Video

## Input

- `podcast.srt` — subtitle file with timing
- `script.md` — full roundtable discussion script

## Output

A `scene_plan` object:

```json
{
  "scenes": [
    {
      "index": 0,
      "speaker": "赵澄圣",
      "start": 0.0,
      "end": 70.369,
      "text": "各位老师好...",
      "visual": "speaker_card",
      "background": "abstract_geology"
    }
  ],
  "speakers": ["赵澄圣", "戴金星", "王国芝", "张水昌"],
  "total_duration": 533.0
}
```

## Process

### 1. Parse SRT

Extract timing and text from each SRT entry:
- `start` / `end` in seconds
- Full spoken text

### 2. Identify speaker per segment

Match each segment to a speaker using the script.md:
- `赵澄圣：text...` → speaker = 赵澄圣
- `戴金星：text...` → speaker = 戴金星
- etc.

### 3. Assign visual treatment

| Speaker | Visual | Background Keyword |
|---------|--------|-------------------|
| Moderator (赵澄圣) | Speaker card + title card | "geology abstract scientific" |
| Expert 1 (戴金星) | Speaker card | "natural gas formation geology" |
| Expert 2 (王国芝) | Speaker card | "reservoir rock formation" |
| Expert 3 (张水昌) | Speaker card | "geochemistry laboratory" |

### 4. Output

Write `scene_plan.json` to the working directory.
