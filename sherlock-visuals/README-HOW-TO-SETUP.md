# 🎬 Sherlock Visual Prompt Engine — Setup & Usage

A dedicated **Claude Project** that turns a finished Sherlock script into
ready-to-paste **image + video prompts** in a consistent **painterly
Victorian-noir** style. It is separate from the script-writing project on
purpose: mixing the two bloats context and causes errors. This one does ONE job
— visuals — and does it reliably for any script you paste.

---

## 📁 What's in this package
```
sherlock-visuals/
├── CLAUDE-PROJECT-INSTRUCTIONS.md   ← paste into the Project "Custom Instructions"
└── knowledge/                       ← upload ALL of these to "Project Knowledge"
    ├── 01-MASTER-STYLE-LOCK.md      ← the painterly Victorian-noir look + fonts
    ├── 02-VIDEO-PROMPT-SYSTEM.md    ← intro / chapter / ending clips (I2V + text)
    ├── 03-IMAGE-PROMPT-SYSTEM.md    ← chapter-wise images (3-beat, sparse budget)
    ├── 04-WORKFLOW-AND-OUTPUT-ORDER.md ← the staged process + chunking rules
    └── 05-WORKED-EXAMPLE.md         ← a full example = the quality benchmark
```

## 🛠️ Setup (5 minutes)
1. claude.ai → Projects → **+ Create Project** → name it **"Sherlock — Visual
   Prompt Engine"**.
2. **Set Custom Instructions** → paste all of `CLAUDE-PROJECT-INSTRUCTIONS.md`.
3. **Project Knowledge / Add Content** → upload all 5 files from `knowledge/`.

---

## ▶️ How to use it (per video)
Open a fresh chat in this project and:

1. **Paste the full finished script** (title + all chapters).
2. Claude returns **STAGE 0 — Visual Asset Breakdown** (theme, palette, the motif
   object, character descriptions, and how many images each chapter gets).
   → review it.
3. Say **"give the videos"** → Claude returns **STAGE 1 — Videos Section**: the
   Intro/Title clip, every Chapter card clip, and the Ending clip — each with an
   IMAGE prompt + a VIDEO (image-to-video) prompt + the on-screen text + font.
4. Say **"chapter 1 images"** → Claude returns that chapter's 2-3 image prompts.
   Then **"chapter 2 images"**, and so on, chapter by chapter.

> Why chapter-by-chapter? A story needs 30-50 image prompts. Claude can't write
> all of them well in one reply (quality decays). Staged = consistently detailed.

---

## ✅ What you can rely on
- Every prompt is **self-contained** (full painterly style baked in — nothing to
  add manually).
- **Theme-accurate** (Claude reads the script first; visuals always match the text).
- **No faces in motion** (only environments/objects/silhouettes animate).
- **Video prompts have no text and no audio** — you add the title text in your
  editor with a vintage serif font (Cinzel / Cormorant / Baskerville / IM Fell).
- **Sparse, sustainable image count** (2-3 per chapter, ~30-50 total).

## 🔗 Pairs with
The **Sherlock "Dispatch Box" script system** (the other project) which writes
the scripts. Workflow: write the script there → paste it here for visuals.
