# 03 — IMAGE PROMPT SYSTEM (Knowledge File)

Images carry the narration body (the bulk of the runtime). They are **sparse on
purpose** — this is an audiobook; fewer images deepen immersion and prevent
creator burnout. Quality and theme-accuracy over quantity.

---

## THE BUDGET (strict)
- **2-3 images per chapter**, maximum **4-5** for a long chapter.
- **30-50 images for the whole story** (e.g. ~30 for a 10-chapter video, up to
  ~50 for a 20-chapter / 2-3 hour epic).
- Pure-dialogue chapters with no new location/clue → fewer images; reuse/re-crop
  rather than force new ones.

## THE 3-BEAT STRUCTURE (where the images go)
Place images on the chapter's story beats, not on a timer:
1. **Establishing shot** (chapter start) — a wide shot of the location/environment
   that sets context.
2. **Tension / interaction shot** (chapter middle) — the confrontation, the
   deduction, the emotional peak (medium / OTS / two silhouettes).
3. **Clue / revelation shot** (chapter end) — an insert/close-up of the new
   evidence or turning point. If the chapter has no new clue, the first two suffice.

For longer chapters add a 4th/5th (e.g. a flashback wide, or a second insert).

## SHOT-GRAMMAR VARIETY (the #1 anti-"mass-produced" signal)
Rotate shot types like a film director — never the same framing repeatedly:
- WIDE / ESTABLISHING · MEDIUM · CLOSE-UP · EXTREME INSERT (clue/object) ·
  OVER-THE-SHOULDER · POV (e.g. through a magnifying glass) · FROM BEHIND /
  SILHOUETTE · FLASHBACK.

## "ONE IMAGE → MULTIPLE FRAMINGS" (anti-static, no extra generation)
For each generated image, suggest 1-2 **re-crops** the editor can use with a slow
Ken Burns move: e.g. *"start wide, then slow punch-in to the brass band."* This
gives several on-screen beats from a single generation — so a sparse image count
never looks static, and the workload stays low.

---

## RULES
- **NO faces as focus / dead stare.** Holmes & Watson from behind, profile,
  silhouette, eyes in shadow. (Faces tolerated only in static images, kept subtle.)
- **Theme-driven:** every image must depict what the narration at that beat
  actually describes — the right location, objects, weather, time of day.
- **Evidence inserts:** when the script reads a letter / shows the clue object /
  the motif, give a detailed readable insert (high-effort signal + motif threading).
- **Character consistency:** describe recurring characters identically; remind the
  user to use `--cref`/seed.
- **Self-contained:** bake the full painterly style block (file 01) into EVERY
  image prompt. Never tell the user to add a suffix.
- Always 2.35:1, chiaroscuro, gritty texture, off-center composition.

---

## OUTPUT FORMAT (per chapter, on the user's command)
```
CHAPTER N — "Title"   (planned: 3 images)

1. WIDE ESTABLISHING
<self-contained painterly image prompt>
(crop: wide → slow push-in to <detail>)

2. MEDIUM / OTS — <the interaction>
<self-contained painterly image prompt>

3. EXTREME INSERT — <the clue/motif>
<self-contained painterly image prompt>
```
Output ONE chapter at a time, then stop and ask for the next. Never dump all
chapters at once. (See file 05 for a worked example.)
