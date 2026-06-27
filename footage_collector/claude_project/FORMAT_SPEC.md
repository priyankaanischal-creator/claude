# FORMAT SPEC — Visual Instructor File (attach this as Project knowledge)

This is the exact format the footage tool parses. Labels are matched
case-insensitively. Lines it READS for searching: `Script Cue (narration):`,
`Visual / Exact Clip to Use:`, `Clip Links:`, `Image Search:`. Lines it IGNORES:
`On-Screen Text:`, `Editor Notes:`.

## Structure
```
TITLE IN CAPS
Topic / context anchor: <Movie Name + Year>

SECTION HEADER (ALL CAPS, no punctuation)
Script Cue (narration): "<exact narration words>"
Visual / Exact Clip to Use: <CAPS SCENE NAME>. "<short quote>". <concrete words>, about <Movie + Year>.
Clip Links: <real youtube url ?t=sec>, <real youtube url 1:23-1:30>      (optional)
Image Search: <term one> | <term two> | <term three>                     (recommended)
```

## How each line is used by the tool
| Line | Used for | Notes |
|------|----------|-------|
| `Script Cue (narration):` | famous short quotes (clip search) | exact script words |
| `Visual / Exact Clip to Use:` | clip + image queries | CAPS scene name = strongest signal |
| `Clip Links:` | tries these exact links FIRST | verified; bad links → auto fallback to search |
| `Image Search:` | image queries (priority) | `|`-separated; concrete visual terms |
| `On-Screen Text:` / `Editor Notes:` | ignored by tool | kept only for a human editor |

## Timestamp formats accepted in Clip Links
- `https://youtu.be/VIDEOID?t=118`  (start at 118s)
- `https://www.youtube.com/watch?v=VIDEOID&t=1m58s`
- `https://youtu.be/VIDEOID 1:23-1:30`  (range)
- `https://youtu.be/VIDEOID @1:23`  (start at 1:23)

## Golden rules
1. Topic anchor MUST include the **year** (disambiguates titles).
2. Visual line ALWAYS starts with a CAPS scene name.
3. Quotes ≤ 6 words.
4. Provide `Image Search:` for every beat. Provide `Clip Links:` only when sure.
5. Real-world beats (history/interviews/posters) → search the real subject.
6. Cover the whole script in order; ~1 beat per 1–3 sentences.
