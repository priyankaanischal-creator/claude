# 04 — WORKFLOW & OUTPUT ORDER (Knowledge File)

How Claude must process a pasted script. The golden rule: **deliver in stages,
never everything at once.** A full story needs 30-50 image prompts plus video
prompts — produced in one reply, quality collapses. Staged = consistently sharp.

---

## STAGE 0 — VISUAL ASSET BREAKDOWN (always first)
When the user pastes the script (title + chapters), read it fully, then output a
SHORT breakdown and stop:

```
VISUAL ASSET BREAKDOWN — "<Title>"
• Core theme / world: ...
• Setting(s): ... (primary + any secondary, e.g. coast + London)
• Palette accent (beyond the base steel-blue/amber): ...
• THE MOTIF object (recurring symbol = thumbnail = often the key clue): ...
• Mood: ...
• Characters (fixed descriptions for consistency): Holmes ... ; Watson ... ; <others>
• Chapter plan (image count each; keep total 30-50):
   Ch1 "<title>" — 3 images
   Ch2 "<title>" — 4 images
   ...
```
End with: "Reply **'give the videos'** for the video prompts, or tell me to adjust."

## STAGE 1 — VIDEOS SECTION (on "give the videos")
Output, in order, with the format from file 02:
- Intro / Title clip (IMAGE + VIDEO prompt + text + font)
- One Chapter card clip per chapter (micro-focus close-ups)
- Ending clip (atmospheric + the motif)
End with: "Reply **'chapter 1 images'** to start the narration images."

> If there are many chapters and the video list is long, it is fine to give the
> Intro + Ending + first ~5 chapter cards, then offer to continue the rest — but
> the videos section is light enough to usually fit in one reply.

## STAGE 2 — IMAGES, CHAPTER BY CHAPTER (on command)
Only when the user says "chapter N images" / "next", output THAT chapter's image
prompts (2-3, max 4-5) using file 03's format, then STOP and say:
"Reply **'chapter <N+1> images'** for the next chapter."
**Never** output more than one chapter of image prompts per reply.

---

## CONSISTENCY ACROSS THE WHOLE JOB
- Keep the SAME painterly style block, palette, and character descriptions from
  Stage 0 through every prompt (no drift between chapters).
- Reuse the recurring-location descriptions identically (Baker Street looks the
  same every time) and remind the user to reuse seeds/`--cref`.
- Keep the MOTIF object threaded: intro → mid-story insert → ending clip.

## SELF-CHECK before sending any prompt
- [ ] Full painterly style block baked in (self-contained)?
- [ ] Matches what the script narrates at that point (theme-accurate)?
- [ ] No face as focus / no dead stare; faces never in video motion?
- [ ] Video prompt: no text, no audio/SFX/voice lines included?
- [ ] Within the image budget (2-3, max 4-5; total 30-50)?
- [ ] Shot type labelled; re-crop suggested where useful?
- [ ] Ended the reply with the exact next command for the user?
