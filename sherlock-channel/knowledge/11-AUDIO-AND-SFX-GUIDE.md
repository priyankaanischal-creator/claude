# 11 — AUDIO & SFX GUIDE (Knowledge File)

Audio is everything in an audiobook. The goal: **maximum atmosphere for minimum
editing effort**. We use a small, fixed library of reusable sounds plus light
music beds — never per-line micro-foley (that way lies a one-week edit per video).

---

## THE PHILOSOPHY: "Minimalist High-Impact Foley"
Use a sound ONLY when it does one of these jobs. **Cap: 20–30 SFX per video.**
1. **Establish a scene** (one ambience layer when a new location begins)
2. **Mark a transition** (door, carriage, train between locations)
3. **Startle / re-grab attention** (glass break, scream, gunshot)
4. **Highlight a crucial clue** (an object set down, a lock turning)
5. **Punch the big reveal** (one suspense sting)
Everything else is carried by the story and the voice.

---

## ⭐ THE FIXED SFX LIBRARY (~35 sounds = your master folder)
Download each ONCE, name the file exactly as the tag. Reuse forever. Claude must
use ONLY these tag names (if a new sound is truly needed, it flags it for you to
add — it must not invent ad-hoc names).

**Ambience / establish:** `baker_street_room` · `winter_wind` · `london_street` ·
`rain_light` · `thunder` · `countryside_birds` · `docks_foghorn` ·
`train_station` · `clock_tick`
**Transitions / doors:** `door_heavy_open` · `door_creak` · `footsteps_wood` ·
`footsteps_cobble` · `horse_carriage` · `horse_hooves` · `train_whistle`
**Startling / action:** `glass_break` · `gunshot` · `door_knock` · `doorbell` ·
`key_drop_table` · `newspaper_throw` · `match_strike` · `liquid_pour` ·
`chair_scrape`
**Human:** `woman_scream` · `man_shout` · `crowd_murmur` · `footsteps_running` ·
`gasp`
**Clue / object:** `coins_jingle` · `lock_turn` · `drawer_open` · `letter_unfold`
· `pocketwatch_click`
**Tension:** `suspense_sting` (reveal) · `heartbeat`

> Source from royalty-free libraries (e.g. free archives / paid packs you own).
> Keep proof of licence. Never rip copyrighted sound.

---

## TAG FORMAT (consistency = fast editing)
Always `[SFX: tag_name]` on its **own line**, never inside a spoken sentence (so
the AI voice never reads it — see file 14). Example in script:

```
The bell rang a few minutes after ten.

[SFX: doorbell]

The woman who was shown up was perhaps thirty, dressed in mourning.
```

---

## BACKGROUND MUSIC BEDS (separate from SFX)
A faint musical underscore, distinct from spot SFX. Keep 3–4 reusable beds:
- `bed_calm` — low, warm strings/piano for Baker Street & reflective scenes
- `bed_tension` — sparse, rising for investigation/suspense
- `bed_dread` — darker, for the danger/climax stretch
- `bed_resolve` — gentle, for the closing/aftermath
Rules: very low in the mix (voice always on top); change the bed at act
boundaries, not constantly; fade, don't cut. Mark with `[MUSIC: bed_tension]` on
its own line. Often silence under the dialogue is best — use beds sparingly.

---

## HOW SFX ARE DELIVERED (the SFX pass, post-script)
After the script is final, Claude does an **SFX pass** and delivers BOTH:
1. **An SFX-tagged version of the script** (tags inserted at the exact lines).
2. **An SFX Cue Sheet** (a checklist) in the Editorial Help file:
```
Total cues: 24  (within the 20–30 cap)
#  | Chapter | Moment                         | Tag
1  | 1       | opening, winter morning        | [SFX: winter_wind]
2  | 1       | Holmes's flame dies            | [SFX: fire_sizzle_out]   ← (add to library)
3  | 1       | Holmes throws down the paper   | [SFX: newspaper_throw]
4  | 2       | the doorbell                   | [SFX: doorbell]
...
```
If a cue needs a sound not in the library, Claude marks it "← add to library" so
you decide whether to download it or swap to an existing one.
