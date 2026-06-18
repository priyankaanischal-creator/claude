# 🕵️ Sherlock Holmes Audiobook Channel — System Setup Guide

This package is a complete, deployable **Claude Project** for running a premium
long-form (1–2 hour) Sherlock Holmes detective audiobook / audio-drama channel
for an English-speaking (US / UK) audience.

It is built to do ONE thing extremely well: produce **deep, original,
un-copyable, NON-repetitive scripts** — at both the big-picture (plot/theme)
level AND the tiny-detail (clue/prop/word) level.

---

## 🎯 The whole strategy in one paragraph

You cannot make individual detective stories "un-copyable" — anyone can write a
mystery. So instead we build an **un-copyable WORLD + SYSTEM**: original
copyrighted characters (a legal moat), deep continuity, airtight fair-play
logic, a recognizable human host ("The Curator"), and an anti-repetition engine
that forces every script to be structurally and texturally different. Copycats
can copy the surface (voice, thumbnail) but never the accumulated world, the
research depth, or the logic. That gap is the moat.

---

## 📁 What's in this package

```
sherlock-channel/
├── README-HOW-TO-SETUP.md            ← this file
├── CLAUDE-PROJECT-INSTRUCTIONS.md    ← paste into the Claude Project "Custom Instructions"
└── knowledge/                        ← upload ALL of these to "Project Knowledge"
    ├── 01-CHANNEL-BIBLE.md           ← identity, frame, host, voice, original characters
    ├── 02-STORY-MATRIX-AND-CATEGORIES.md  ← 14 case categories + the "dials"
    ├── 03-FORMAT-LIBRARY.md          ← 17 video formats + rotation rules
    ├── 04-ANTI-REPETITION-SYSTEM.md  ← macro + micro anti-repetition engine
    ├── 05-SCRIPTING-PIPELINE.md      ← modular blueprint → chapter → polish prompts
    ├── 06-TITLE-AND-THUMBNAIL-SYSTEM.md  ← rotating titles + object thumbnails
    ├── 07-VICTORIAN-ASSET-BANK.md    ← 200+ props/settings (defeats "teacup" defaults)
    ├── 08-EPISODE-LEDGER.md          ← the external memory (auto-updated each episode)
    ├── 09-UNTOLD-CASES-MASTERLIST.md ← 35 Doyle-referenced cases = episode pipeline
    ├── 10-EDITORIAL-HELP-GUIDE.md    ← titles, description, tags, quizzes, SFX, outro
    ├── 11-AUDIO-AND-SFX-GUIDE.md     ← fixed SFX library + music beds (low-effort)
    ├── 12-META-ARC-AND-CHARACTER-BIBLE.md ← "The Bell" arc + original cast continuity
    ├── 13-STYLE-SAMPLE.md            ← the VOICE anchor (Claude matches this)
    └── 14-TTS-NARRATION-RULES.md     ← clean AI-voiceover writing rules
```

---

## 🛠️ Setup (5 minutes)

1. Go to **claude.ai → Projects → + Create Project**.
2. Name it: **"Sherlock — Dispatch Box Scripts"**.
3. Open **Set Custom Instructions** → paste ALL of `CLAUDE-PROJECT-INSTRUCTIONS.md`. Save.
4. Open **Project Knowledge / Add Content** → upload all 14 files from `knowledge/`.
5. Done.

---

## ▶️ How to write ONE episode (the golden rule)

> **NEVER ask for a full 1–2 hour script in a single prompt.** AI "decays" after
> ~20 minutes of content (it loops, repeats clues, forgets details). Always work
> in the 3-step modular pipeline below. This is non-negotiable.

**For every new episode, open a FRESH chat** (so no prose bleeds from the last
script), **attach the latest Ledger**, then:

1. **Pick the dials** (5 min) — OR just type *"write a new script"* and let Claude
   choose fresh dials from the Ledger. Optionally specify word count, parts,
   category, or format and Claude will follow exactly. (Dials = format, category,
   setting, motive, solution-trick, + 3–5 props from `07`; cooldowns in `08`.)
2. **Blueprint** (`05`) — outline + clue→payoff ledger + title options. Review it.
3. **Chapters** — "write Chapter 1" … then "continue" for each (~1,500 words).
   The intro is written here as a rotating in-world cold open (narrated, no face).
4. **Polish + de-dup + TTS + fact-check** (`05`, `14`).
5. **Post-script package** — Claude returns the SFX-tagged script, the Editorial
   Help file (titles/description/tags/quizzes/thumbnail/SFX cues), outro
   talking-points, and the **auto-updated Ledger**.
6. **Save the updated Ledger** (and its backup) for next time.

> Your only manual work: attach the Ledger, type "continue" a few times, pick a
> title, and save the returned Ledger. Everything else is automatic.

---

## 📏 Length math (memorize)

- Narration ≈ **150 words / minute**
- **1 hour ≈ 9,000–10,000 words**
- **2 hours ≈ 18,000–20,000 words**

So a 2-hour episode = ~18k+ words = **must** be built chapter-by-chapter, and is
a great candidate to split into **Part 1 / Part 2** (cliffhanger) once you have
subscribers.

---

## 🎬 The channel's video shape (default)

```
[INTRO]   — in-world, AI-narrated, NO face. 1–5 min. Rotate the intro TYPE
            (teaser / hook-question / case-file / atmospheric / 5-min overview /
            listener-challenge / voice-only Curator). Vary when the story begins.
[STORY]   — IMMERSIVE CASE — AI voice + clips, the full uninterrupted story
[OUTRO]   — YOUR face (the only on-camera part): spoken in your own words from
            3–5 story-specific talking-points, rotating the angle each video
            (did-you-guess / character / what-next / theory / behind-the-scenes /
            reply-to-comment / real-history).
```

The human OUTRO = your authenticity signal (anti "mass-produced AI content"
demonetization). Add to every video description: *"Original story. Narration
uses an AI voice."*

---

## 💾 Protect the Ledger (critical)
The Ledger is the system's entire memory. **Keep two copies** (computer + cloud)
and update the backup after every episode. Lose it = lose the channel's
non-repetition memory.

---

## ⚠️ Three hard safety rules (protect monetization)

1. **No real graphic crimes** (no Ripper / Thames Torso / real victims). Use real
   history only as *texture* (places, inventions, scandals) — never center real
   gore. Keep cases fictional.
2. **No graphic gore** in autopsies/medical detail — focus on deduction, not blood.
3. **Be transparent** about AI narration in the description.
