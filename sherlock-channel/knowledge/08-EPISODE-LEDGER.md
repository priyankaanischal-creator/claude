# 08 — EPISODE LEDGER (Knowledge File) — the SYSTEM'S MEMORY

Claude has amnesia between chats. The Ledger is the channel's **external memory**:
it records what every past episode used, so the next one never repeats it. This
single file is what makes "zero repetition" possible.

> **Golden loop:** Each new episode → attach the latest Ledger → Claude reads it,
> writes a fresh episode, and **automatically outputs the updated Ledger** (with
> the new row added). You save it. Next episode → attach that version. Repeat.

---

## ⚠️ BACKUP RULE (do not skip)
The whole system depends on this one file. **Keep at least two copies** (e.g. on
your computer AND in Google Drive/Dropbox), and update the backup after every
episode. If you lose the Ledger, you lose the channel's memory. Treat it like the
master key.

---

## WHAT CLAUDE DOES AUTOMATICALLY
At the end of every completed episode, Claude outputs the **full updated Ledger**
in two forms:
1. A readable **Markdown table** (to glance at), and
2. A **CSV block** (to paste/save as `ledger.csv` and open in Excel/Sheets).
You never hand-update it.

---

## COLUMNS

### Macro (structure)
`Ep# · Title · TitleFormat · Intro-Type · Format · Category · Structure ·
Setting · Victim/Client · CentralLie · Motive · SolutionTrick · Misdirection ·
RedHerringType · EndingTone · SensoryLens · OriginalChars · MetaArcBeat ·
OutroAngle`

### Micro (the repetition-killers)
`HeroProp · SupportProps · KeyClue · Method/Weapon · CauseOfDeath ·
Holmes'sMethod · NotablePhrases/Images · ThumbnailObject`

### Tracking
`Performance/Lessons` (views, comments, what worked — to improve over time)

---

## CSV HEADER (copy this as row 1 of `ledger.csv`)
```
Ep,Title,TitleFormat,IntroType,Format,Category,Structure,Setting,Victim,CentralLie,Motive,SolutionTrick,Misdirection,RedHerringType,EndingTone,SensoryLens,OriginalChars,MetaArcBeat,OutroAngle,HeroProp,SupportProps,KeyClue,Method,CauseOfDeath,HolmesMethod,NotableImages,ThumbnailObject,Lessons
```

## SAMPLE ROW (Markdown)
| Ep | Title | Format | Category | Structure | Setting | Motive | Trick | SensoryLens | HeroProp | KeyClue | Method | Notes |
|----|-------|--------|----------|-----------|---------|--------|-------|-------------|----------|---------|--------|-------|
| 007 | The Clockmaker's Silence | Dispatch Box | Cipher | Locked-room | clockmaker's workshop | guild revenge | timing | SOUND | brass escapement | a missed chime | blocked flue | strong CTR; pin "did you hear it?" |

---

## COOLDOWN RULES (enforce when picking dials)
- **Setting:** no repeat for **10** episodes
- **Solution trick:** no repeat for **15** episodes
- **Method/weapon:** no repeat for **15** episodes
- **Hero prop:** no repeat for **12** episodes
- **Motive category:** no repeat for **6** episodes
- **Mystery structure:** rotate — never 3 of the same in a row
- **Format:** never back-to-back; specials have a **6**-episode cooldown
- **Title format & Intro-Type & Outro-Angle:** never the same as the previous ep

## HOW THE BURN LIST IS BUILT
Before each episode, take the **last 10 rows** and collect their Settings, Hero
Props, Key Clues, Methods, and Notable Images → that becomes the **BURN LIST**
you paste into the prompts (file 05). Permanent cliché bans (file 04) are added
on top.

---

## INSTRUCTION TO CLAUDE (built into the system)
> "Whenever an episode is completed, append its full row to the Ledger and output
> the entire updated Ledger as both a Markdown table and a CSV block, with no
> commentary in between, ready to save."
