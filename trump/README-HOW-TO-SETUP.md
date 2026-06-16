# 🇺🇸 How to Set Up Your Claude Project — "Trump Poll-Image Generator"

This package turns Claude into a machine that, when you type **names or theme
keywords**, gives you back:
1. 🎨 a **detailed, crop-safe 4:5 image prompt** (for ChatGPT / Gemini / Midjourney),
2. 📝 a **~100-word patriotic Facebook caption**, and
3. #️⃣ **4–5 hashtags**.

Built for a high-volume dedicated Trump fan page with **automatic
theme/era/scene/colour variation** (millions of combinations) so content never
repeats.

- **2 items → 2-panel poster** • **3 items → 3-panel** • **4 items → 2×2 grid**
- **1 name (e.g. "Trump") → a multi-era timeline poster**
- **Theme keywords** work too: `Trump army`, `Trump WWE`, `Trump golf`, `Trump 80s`,
  `Trump family`, `Trump & JD Vance`.

---

## 📁 What's in this package
```
trump/
├── TRUMP-PROJECT-INSTRUCTIONS.md     ← paste into the Project's "Custom Instructions"
├── README-HOW-TO-SETUP.md            ← this file
└── knowledge/                        ← upload ALL of these to "Project Knowledge"
    ├── 01-PROMPT-MASTER-TEMPLATE.md      (2/3/4-char skeletons + crop-safe block + AI-ART tag)
    ├── 02-THEME-STYLE-LIBRARY.md         (eras, scenes, styled-as, Army/WWE/golf/gala themes)
    ├── 03-FONT-AND-COLOR-GUIDE.md        (patriotic headers, palettes, fonts, voting systems)
    ├── 04-CAPTION-AND-HASHTAG-GUIDE.md   (~100-word caption + hashtag rules)
    ├── 05-EXAMPLES.md                    (full worked timeline / army / themes / family examples)
    └── 06-TRUMP-CHARACTER-BANK.md        (Trump eras, family, allies, past presidents)
Trump-Name-Bank.xlsx                  ← 3 sheets × 100 ready-to-paste combinations
```

---

## 🛠️ Step-by-step setup (about 5 minutes)
1. Go to **claude.ai** → sidebar → **Projects** → **+ Create Project**.
2. Name it: **"Trump Poll-Image Generator"**.
3. Open the project → **Set custom instructions** →
   open `TRUMP-PROJECT-INSTRUCTIONS.md`, copy ALL of it, paste, **Save**.
4. Open **Project knowledge / Add content** → upload all **6 files** from
   `knowledge/`. (If upload isn't available on your plan, paste each file's text
   as a separate knowledge doc.)
5. Done. Your generator is ready.

> Keep this as a SEPARATE project from your UK Royal Family one — different
> instructions and knowledge files.

---

## ▶️ How to use it daily (your only job = type names/themes)
Open the project and type. Examples:
- `Trump`                                  → multi-era timeline poster
- `Trump army`                             → patriotic military themed poster
- `Trump golf, Trump WWE, Trump gala`      → 3-panel "showman" poster
- `Trump vs Reagan`                        → "favourite President?" poll
- `Donald, Melania, Ivanka, Don Jr`        → 4-character family grid
- `Trump & JD Vance`                       → "dream team" poster

Claude replies with a `🎲 Variation:` line + 3 sections:
1. 🎨 IMAGE PROMPT → paste into your image generator.
2. 📝 FACEBOOK CAPTION → ~100 words, ready to post.
3. #️⃣ HASHTAGS → 4–5 tags.

### Want a specific look? Just add it after the names:
- `Trump — army theme, flag studio, vintage poster style`
- `Trump vs Lincoln vs Washington — favourite President, oil-painting style`
- `Trump family — Mar-a-Lago gala, black & gold`
If you say nothing, Claude auto-picks a fresh random combo each time.

---

## 📐 THE 4:5 SIZE FIX (the most important part — read this!)
ChatGPT often outputs a canvas **taller than 4:5** (e.g. 1003×1568). When you crop
to **4:5 (1080×1350)**, the crop removes strips from the **TOP and BOTTOM** — that's
why text/faces used to get cut.

**The prompts now solve this automatically** by reserving a solid-colour blank band
on the **top ~15%** and **bottom ~15%**, and keeping all headlines, labels and
figures in the safe centre. So when you crop:
1. Open the generated image in any cropper (Canva / Photopea / phone editor).
2. Choose **4:5** (or 1080×1350).
3. Centre the crop vertically (equal top/bottom).
4. Only the blank top/bottom bands get trimmed — **nothing important is lost.** ✅

---

## ⚠️ RESPONSIBLE-USE (keeps your page safe & online)
The instructions build these in automatically, but keep them in mind:
- Content is **opinion/admiration fan-art** — every prompt adds a small **"AI ART"**
  tag so viewers don't mistake it for a real photo.
- **No fake news or fabricated events** (no invented arrests, fake documents, etc.).
- **No hate, mockery, or attacks** — even in rival comparisons, keep a respectful
  "who do you support?" tone.
- Following these keeps you within Facebook's rules and avoids takedowns.

---

## 💡 Pro tips for the BEST, most realistic results
- Use an image model that follows long prompts well (ChatGPT/GPT-4o image or
  Gemini work great for this poster style).
- For accurate faces, also UPLOAD a clear reference photo and add: "use this face."
- If text looks blurry: "make the headline and name labels bigger, bolder and
  perfectly readable."
- If the top/bottom band is missing: "add a solid [colour] band across the top 15%
  and bottom 15% with nothing important in them."
- Rotate through the `Trump-Name-Bank.xlsx` combos so you never run dry.

---

## 🔁 Why your feed never runs out
The instructions force Claude to rotate **people × era × theme × scene × visual
style × header × palette × voting system** every time — that's **millions** of
combinations. Even posting several times a day, you won't repeat for years.

### 📅 Suggested weekly content pillars
- **Mon** Timeline ("Which era of Trump?") • **Tue** Family • **Wed** Styled fan-art
  (Army/cowboy/hero) • **Thu** Favourite-President polls • **Fri** Dream team •
  **Sat** Signature themes (golf/WWE/gala) • **Sun** Engagement ("Rate this / Caption this")

Enjoy! 🇺🇸🦅
