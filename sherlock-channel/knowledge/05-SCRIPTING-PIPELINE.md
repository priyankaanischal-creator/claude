# 05 — SCRIPTING PIPELINE (Knowledge File)

How to actually produce a 1–2 hour script without quality collapse. Copy-paste
prompts are provided. **Always open a FRESH chat per episode** (file 04, Fix 7).

---

## LENGTH MATH (memorize)
- Narration ≈ **150 words/minute**
- 1 hour ≈ **9,000–10,000 words** · 2 hours ≈ **18,000–20,000 words**
- A 2-hour case = ~12–16 chapters of ~1,200–1,800 words each.

> ❌ Never generate the whole script in one prompt (token decay → loops/repeats).
> ✅ Always: Blueprint → Chapter-by-chapter → Polish.

---

## STEP 0 — FILL THE EPISODE SPEC (you, ~5 min)
Open the Ledger (file 08), check cooldowns, and fill the dials (file 02). You'll
paste this Spec into the blueprint prompt. Example Spec:

```
EPISODE: 007
FORMAT: Dispatch Box (C2)
CASE CATEGORY: 4 — Cipher / pattern
MYSTERY STRUCTURE: Locked-room
SETTING: A clockmaker's workshop above a railway arch, Clerkenwell
VICTIM/CLIENT: A deaf engraver found dead beside a stopped regulator clock
CENTRAL LIE: "He died of a seizure, alone, doors bolted from inside."
REAL MOTIVE: Decades-old guild revenge (not money)
METHOD/WEAPON: [from Asset Bank]
MISDIRECTION: false timeline
SOLUTION TRICK: timing (the clock was the alibi machine)
RED HERRING: a rival engraver with a public grudge (psychological)
ENDING TONE: bittersweet
SENSORY LENS: SOUND (ticking patterns, silences, a missed chime)
ASSIGNED PROPS (only these atmospheric objects): brass escapement,
  acid-etching tray, a tuning fork, a ledger of repairs, iron filings
ORIGINAL CHARACTERS: Constable Aggie Finch; cameo Mr. Cobb
BURN LIST (do not use): [paste permanent list + last-10-episode items]
```

---

## STEP 1 — BLUEPRINT PROMPT (1 prompt)

```
You are the Sherlock Dispatch Box script engine. Using the EPISODE SPEC below
and the project knowledge files, produce a BLUEPRINT only — no prose yet.

[PASTE EPISODE SPEC]

Deliver:
1. LOGLINE (1 sentence).
2. CAST (canon + assigned original characters) with one-line distinct voices.
3. CHAPTER LIST (12–16 chapters) — for each: title, purpose, ~word target,
   what changes, and the chapter-ending hook.
4. CLUE → PAYOFF LEDGER: every clue Holmes will use in the solution, the exact
   chapter it is PLANTED, and the chapter it PAYS OFF. (Fair-play: every solution
   clue must be planted earlier.)
5. THE CENTRAL LIE and the TRUE sequence of events (for your own consistency).
6. RED HERRINGS (with why each is misleading and how it's dismissed).
7. The "CAN YOU SOLVE IT?" beat placement (just before the reveal).
8. Where the meta-arc ("The Bell") is lightly seeded, if at all.

Rules: respect the BURN LIST; derive atmosphere only from the SETTING and
ASSIGNED PROPS; no banned AI words. Keep all real-world facts verifiable.
```

→ Review/adjust the blueprint. This is where you control quality cheaply.

---

## STEP 2 — CHAPTER PROMPT (repeat per chapter)

```
Write CHAPTER [N] only: "[chapter title]".
Target length: [1,200–1,800] words.
Purpose & ending hook: [from blueprint].
POV/voice: Dr. Watson (warm, a step behind Holmes).
SENSORY LENS for this episode: [e.g. SOUND] — lead with it.
Use ONLY these atmospheric props: [assigned props]. Invent no new objects;
if you need one, stop and ask me.
BURN LIST (forbidden): [paste]. Banned AI words: [paste].
Plant exactly these clues here (per the ledger): [clues for chapter N].
Do NOT reveal the solution. End on the specified hook.
Maintain continuity with what came before; do not re-summarize prior chapters.
```

Tips:
- Feed the **previous chapter's last ~200 words** as context if continuity drifts.
- Vary chapter rhythm (per-chapter "BPM"): alternate slow-burn and fast chapters.
- For dialogue, use action-reaction (characters interrupt/cross-question), not
  long monologues.

---

## STEP 3 — POLISH / DE-DUPLICATION PASS (1–2 prompts per part)

```
Here is the assembled draft of Episode [N]. Do a QUALITY + DE-DUP pass. Output a
revised version plus a short report.

CHECKS:
1. FAIR-PLAY: confirm every solution clue was planted earlier (cite chapters).
   Flag any clue that appears only at the reveal.
2. CONTINUITY: names, timeline, injuries, props, character voices consistent.
3. CLICHÉ PROPS: list all physical objects/sensory details; replace any banned
   cliché (teacup, fog, candle, etc.) with setting-specific alternatives.
4. AI WORDS: find/replace all banned vocabulary with plain period prose.
5. REPETITION: flag any repeated phrase/image used 3+ times; vary them.
6. CHARACTER VOICE: ensure each character speaks distinctly.
7. PACING: note any saggy stretch; tighten.
8. FACT-CHECK: flag any technical/historical claim I should verify.
```

---

## STEP 4 — POST-SCRIPT PACKAGE (Claude delivers all at once)
After the final polished script, Claude outputs in one bundle:
- The **SFX-tagged script** (file 11) + the **SFX cue sheet**.
- The **Editorial Help file** (file 10): title options, description with chapter
  markers, video tags, 2 quizzes, thumbnail concept.
- **Outro talking-points** (3–5 story-specific, rotating angle — file 10).
- The **auto-updated Ledger** (file 08) as a Markdown table AND a CSV block.

Then the user saves the script and the Ledger (+ backup) for next time.

---

## OPTIONAL — PARTS
If splitting into Part 1 / Part 2: end Part 1 on the Act-1 or Act-2 cliffhanger
from the blueprint. Run Steps 2–3 per part. Keep each part ~45–70 min.

---

## ONE-OFF — SEED / EXPAND THE ASSET BANK (separate chat)
When the Asset Bank runs low, in a SEPARATE chat:
```
Brainstorm 50 obscure, period-accurate Victorian [objects / professions /
murder methods / settings] suitable as detective-story clues. Avoid all common
tropes (teacups, letters, candles, fog, generic poisons). For each, one line on
why it could matter in a case. Make them specific and unusual.
```
Then paste the good ones into file 07 and mark them unused.
