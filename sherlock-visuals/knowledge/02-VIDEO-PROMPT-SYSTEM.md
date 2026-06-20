# 02 — VIDEO PROMPT SYSTEM (Knowledge File)

Video clips are used at only THREE kinds of moments (the rest is images):
1. **Intro / Title** clip (one per video)
2. **Chapter card** clip (one per chapter)
3. **Ending** clip (one per video)

For EACH clip you deliver three things: an **IMAGE prompt**, a **VIDEO prompt**,
and the **on-screen text + font**.

---

## THE IMAGE→VIDEO (I2V) METHOD — always
Text-to-video hallucinates and breaks the theme. So:
1. First generate a perfect, theme-accurate **static image** (full control) from
   the IMAGE prompt (Midjourney / Leonardo), in the painterly style (file 01).
2. Then feed that image into a video tool (Runway / Kling / Luma) using the
   **VIDEO prompt**, which adds only **camera motion + subtle scene motion**.
This keeps "Baker Street" as Baker Street — no morphing of the place.

---

## RULES FOR THE VIDEO PROMPT
- Describe **camera motion** (slow push-in / drift / very slow zoom) and **subtle
  scene motion** (drifting fog, swelling sea, flickering light, faint feather/dust).
- Keep motion **minimal and smooth** — explicitly forbid morphing/warping/distortion.
- **NO faces animated.** Use environments, objects, silhouettes, backs.
- End every VIDEO prompt with: *"Absolutely no text, no letters, no words, no
  captions, no watermark anywhere in the frame. No audio, no music, no voice, no
  sound effects."* (Text is added later in the editor; SFX/voice are done separately.)
- Always cinematic **2.35:1 widescreen**; hold the painterly look, film grain,
  palette throughout.

## TEXT IS ADDED IN THE EDITOR (not generated)
AI video tools cannot spell reliably. So generate a CLEAN clip, then overlay text
in the editor. For each clip provide:
- The **exact on-screen text** (e.g. `Chapter One — "The Turning Tide"`).
- **Font** (file 01): Cinzel / Trajan for the title; Cormorant Garamond / IM Fell
  English for chapter cards. Cream/off-white, centred, letter-spaced, subtle
  shadow, slow fade in/out.

---

## WHAT EACH CLIP SHOULD BE

### Intro / Title clip
- A **wide, atmospheric establishing shot** of the story's core location/mood
  (derived from the script) — e.g. a fog-bound coast, a gas-lit street, a lonely
  manor. Slow cinematic push-in. Sets the whole tone in the first 10-15 seconds.
- Text: the video TITLE.

### Chapter card clips (one per chapter)
- A **micro-focus close-up** tied to that chapter's content (AI video does
  close-ups far better than wide/crowd shots, which morph). E.g. a chapter called
  "The Bloody Blade" → a candlelit close-up of a knife on a wooden floor, not a
  whole murder scene.
- Keep it thematic to the chapter; reuse the channel look.
- Text: `Chapter N — "Chapter Title"`.

### Ending clip
- A **quiet, resolved atmospheric shot** that often features the episode's **MOTIF
  object** (the recurring symbol) — e.g. the clue object placed in an evidence box.
  Leads into the creator's face-cam outro.
- Text: optional short closing line, or none.

---

## OUTPUT FORMAT (per clip)
```
■ INTRO / TITLE
IMAGE PROMPT:
<self-contained painterly image prompt>

VIDEO PROMPT (image-to-video):
<camera + subtle motion; no text; no audio>

ON-SCREEN TEXT:  THE <TITLE>
FONT:  Cinzel / Trajan, cream, centred, letter-spaced, slow fade
```
Repeat for each Chapter card and the Ending. (See file 05 for a worked example.)
