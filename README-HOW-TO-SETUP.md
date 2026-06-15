# 🚀 How to Set Up Your Claude Project — "Royal Family Poll-Image Generator"

This package turns Claude into a machine that, when you type **royal family names**,
gives you back:
1. 🎨 a **detailed, crop-safe 4:5 image prompt** (for ChatGPT / Gemini / Midjourney),
2. 📝 a **~100-word Facebook caption**, and
3. #️⃣ **4–5 hashtags**.

Built for high-volume posting (1000s of "Who is your favourite?" comparison
posters) with **automatic style/era/scene/colour variation** so nothing repeats.

- **2 names → 2-character poster** (2 panels)
- **3 names → 3-character poster** (3 panels)
- **4 names → 4-character poster** (2×2 grid)

---

## 📁 What's in this package
```
claude/
├── CLAUDE-PROJECT-INSTRUCTIONS.md   ← paste into the Project's "Custom Instructions"
├── README-HOW-TO-SETUP.md           ← this file
└── knowledge/                       ← upload ALL of these to "Project Knowledge"
    ├── 01-PROMPT-MASTER-TEMPLATE.md     (2/3/4-char prompt skeletons + crop-safe block)
    ├── 02-THEME-STYLE-LIBRARY.md        (eras, scenes, outfits, moods — the variety engine)
    ├── 03-FONT-AND-COLOR-GUIDE.md       (header styles, palettes, fonts, voting systems)
    ├── 04-CAPTION-AND-HASHTAG-GUIDE.md  (~100-word caption + hashtag rules)
    ├── 05-EXAMPLES.md                   (full worked 2/3/4-character examples)
    └── 06-ROYAL-CHARACTER-BANK.md       (how to describe each royal accurately)
```

---

## 🛠️ Step-by-step setup (about 5 minutes)
1. Go to **claude.ai** → sidebar → **Projects** → **+ Create Project**.
2. Name it: **"Royal Family Poll-Image Generator"**.
3. Open the project → **Set custom instructions** →
   open `CLAUDE-PROJECT-INSTRUCTIONS.md`, copy ALL of it, paste, **Save**.
4. Open **Project knowledge / Add content** → upload all **6 files** from
   `knowledge/`. (If upload isn't available on your plan, paste each file's text
   as a separate knowledge doc.)
5. Done. Your generator is ready.

---

## ▶️ How to use it daily (your only job = type names)
Open the project and type names. Examples:
- `Diana & Anne`                              → 2-character poster
- `Camilla, Diana, Meghan`                    → 3-character poster
- `Kate & Meghan & Sophie & Zara`             → 4-character (2×2 grid)
- `Charles & Camilla vs William & Kate`       → couple-vs-couple (2 panels)

Claude replies with a `🎲 Variation:` line + 3 sections:
1. 🎨 IMAGE PROMPT → paste into your image generator.
2. 📝 FACEBOOK CAPTION → ~100 words, ready to post.
3. #️⃣ HASHTAGS → 4–5 tags.

### Want a specific look? Just add it after the names:
- `Diana & Kate — vintage 1950s, garden`
- `William & Harry — military uniform, navy & gold`
- `George & Charlotte & Louis — childhood theme`
If you say nothing, Claude auto-picks a fresh random combo each time.

---

## 📐 THE 4:5 SIZE FIX (the most important part — read this!)
ChatGPT often outputs a canvas **taller than 4:5** (e.g. 1003×1568). When you crop
to **4:5 (1080×1350)**, the crop removes strips from the **TOP and BOTTOM** — that's
why text/faces used to get cut.

**The prompts now solve this automatically** by reserving a solid-colour blank band
on the **top ~15%** and **bottom ~15%**, and keeping all headlines, labels, and
people in the safe centre. So when you crop:

1. Open the generated image in any cropper (Canva / Photopea / phone editor).
2. Choose **4:5** (or 1080×1350).
3. Centre the crop vertically (equal top/bottom).
4. Only the blank top/bottom bands get trimmed — **nothing important is lost.** ✅

---

## 💡 Pro tips for the BEST results
- Use an image model that follows long prompts well (ChatGPT/GPT-4o image or
  Gemini work great for this poster style).
- For accurate faces, also UPLOAD a clear reference photo of each royal to the
  image tool and add: "use this exact face."
- If text looks blurry: tell the tool "make the headline and name labels bigger,
  bolder and perfectly readable."
- If the top/bottom band is missing: add "add a solid [colour] band across the top
  15% and bottom 15% with nothing important in them."
- Keep it **respectful and flattering** — these are affectionate fan polls.

---

## 🔁 Why your feed stays fresh
The instructions force Claude to rotate **era × scene × outfit × header × palette
× voting system** every time (hundreds of thousands of combinations), so even
1000s of posts won't look repetitive.

Enjoy! 👑
