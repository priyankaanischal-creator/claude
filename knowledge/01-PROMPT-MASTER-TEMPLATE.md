# 01 — PROMPT MASTER TEMPLATE (Knowledge File)

This file gives the EXACT skeletons Claude must follow when writing the image
prompt. Fill every `[ ]` with vivid, specific detail. **Never leave a blank.**

Three skeletons: **2-character**, **3-character**, **4-character (2×2 grid)**.
Every skeleton already contains the **CROP-SAFE 4:5 block** — keep it word-for-word
and only swap the `[colour]`/`[detail]` parts.

---

## ⭐ THE CROP-SAFE 4:5 BLOCK (goes at the TOP of EVERY prompt)
```
Create a vertical portrait image. Design ALL content inside a centred 4:5 safe
zone (final crop = 1080 x 1350 px, ratio 4:5). The source canvas may render
TALLER than 4:5, so the TOP and BOTTOM strips WILL be cropped off — therefore:
- TOP ~15% = a solid [BAND COLOUR] band with NOTHING important in it.
- BOTTOM ~15% = a solid [BAND COLOUR] band with NOTHING important in it.
- Put the headline BELOW the top band; put all name labels ABOVE the bottom band.
- Keep every person's head and feet/hemline well inside the central zone.
- The left and right edges are safe (only top/bottom get cropped).
Make the top/bottom band colour match the design so a crop looks seamless.
```
> Set `[BAND COLOUR]` to match the chosen header/theme (navy theme → navy bands,
> cream theme → cream bands, black theme → black bands, etc.).

---

## ▶ 2-CHARACTER SKELETON (user gave 2 names)
```
[CROP-SAFE 4:5 BLOCK with band colour = [BAND COLOUR]]

THEME: [ERA/STYLE] • [COLOUR PALETTE] • [overall mood].

LAYOUT: The central safe zone is split vertically into TWO equal panels with a
[thin gold / silver / white / no] divider.

HEADLINE (upper-central area, below the top band): a [HEADER STYLE] band with
[ornament + small crown?] and [FONT] text reading "[HEADLINE WORDING]". Keep the
text centred and away from the side edges.

LEFT PANEL (A):
- Photorealistic [full-body / seated / candid] portrait of [PERSON 1 — accurate
  description: approx age, hair, build], wearing [OUTFIT 1 details: colour,
  garment, accessories, hat/jewellery]. [POSE], [EXPRESSION].
- Background: [SCENE/LOCATION detail 1], [lighting].

RIGHT PANEL (B):
- Photorealistic [same pose type] portrait of [PERSON 2 — accurate description],
  wearing [OUTFIT 2 — same family/style as panel 1 for harmony], [POSE], [EXPRESSION].
- Background: [SCENE/LOCATION detail 2 — same setting family for consistency], [lighting].

NAME LABELS (lower-central area, above the bottom band): [LABEL STYLE] for each —
Left: [voting marker e.g. circle "A" / 👍 / "1st"] + "[PERSON 1 NAME]" in
[font + colour]. Right: [voting marker e.g. circle "B" / ❤️ / "2nd"] +
"[PERSON 2 NAME]" in [font + colour]. [Optional subtitle/title under each name.]

STYLE: photorealistic editorial portrait photography, 85mm lens, soft CONSISTENT
lighting across both panels, identical pose and framing, ultra-detailed, 8K.
Avoid: wrong aspect ratio, important content near the very top or bottom edge,
distorted faces, extra fingers, blurry or unreadable text, watermark.
```

---

## ▶ 3-CHARACTER SKELETON (user gave 3 names)
```
[CROP-SAFE 4:5 BLOCK with band colour = [BAND COLOUR]]

THEME: [ERA/STYLE] • [COLOUR PALETTE] • [overall mood].

LAYOUT: The central safe zone is split into THREE equal vertical panels with
[thin gold / white / no] dividers.

HEADLINE (upper-central area, below the top band): a [HEADER STYLE] band with
[ornament + small crown?] and [FONT] text reading "[HEADLINE WORDING]" (may be on
two lines, second line a different accent colour). Centred, away from side edges.

LEFT PANEL:
- Photorealistic [pose type] portrait of [PERSON 1 — accurate description],
  wearing [OUTFIT 1], [POSE], [EXPRESSION]. Background: [SCENE detail 1], [lighting].

CENTER PANEL:
- Photorealistic [same pose type] portrait of [PERSON 2 — accurate description],
  wearing [OUTFIT 2 — same style family], [POSE], [EXPRESSION].
  Background: [same SCENE family], [lighting].

RIGHT PANEL:
- Photorealistic [same pose type] portrait of [PERSON 3 — accurate description],
  wearing [OUTFIT 3 — same style family], [POSE], [EXPRESSION].
  Background: [same SCENE family for consistency], [lighting].

NAME LABELS (lower-central area, above the bottom band): three [LABEL STYLE] boxes —
"[PERSON 1 NAME]" ([colour 1]), "[PERSON 2 NAME]" ([colour 2]),
"[PERSON 3 NAME]" ([colour 3]); with [voting markers: A/B/C OR 👍❤️😮 OR 5-star
rows OR small crowns]. [Optional title under each name.]

STYLE: photorealistic editorial portrait photography, 85mm lens, soft CONSISTENT
lighting across all three panels, identical pose and framing, ultra-detailed, 8K.
Avoid: wrong aspect ratio, important content near the very top or bottom edge,
distorted faces, extra fingers, blurry or unreadable text, watermark.
```

---

## ▶ 4-CHARACTER SKELETON (user gave 4 names → 2×2 grid)
```
[CROP-SAFE 4:5 BLOCK with band colour = [BAND COLOUR]]

THEME: [ERA/STYLE] • [COLOUR PALETTE] • [overall mood].

LAYOUT: The central safe zone is a 2x2 GRID of four equal panels with [thin
gold / white] dividers. (Headline sits above the grid, labels below it — all
inside the central zone.)

HEADLINE (upper-central area, below the top band): a [HEADER STYLE] band with
[ornament + small crown?] and [FONT] text reading "[HEADLINE WORDING]". Centred.

PANEL 1 (top-left): Photorealistic [pose] portrait of [PERSON 1 — description],
wearing [OUTFIT 1], [EXPRESSION]. Background: [SCENE detail].
PANEL 2 (top-right): [PERSON 2 — description], wearing [OUTFIT 2], [EXPRESSION].
Background: [same SCENE family].
PANEL 3 (bottom-left): [PERSON 3 — description], wearing [OUTFIT 3], [EXPRESSION].
Background: [same SCENE family].
PANEL 4 (bottom-right): [PERSON 4 — description], wearing [OUTFIT 4], [EXPRESSION].
Background: [same SCENE family for consistency].

NAME LABELS (lower-central area, above the bottom band): four small [LABEL STYLE]
plates: "[NAME 1]", "[NAME 2]", "[NAME 3]", "[NAME 4]" with [voting markers:
A/B/C/D OR small reaction icons OR 5-star rows]. Keep all heads inside the grid,
away from top/bottom edges.

STYLE: photorealistic editorial portrait photography, 85mm lens, soft CONSISTENT
lighting across all four panels, identical pose and framing, ultra-detailed, 8K.
Avoid: wrong aspect ratio, important content near the very top or bottom edge,
distorted faces, extra fingers, blurry or unreadable text, watermark.
```

---

## ▶ COUPLE-VS-COUPLE NOTE
If a panel holds a couple (e.g. "Anne & Sir Timothy" vs "Charles & Camilla"),
treat it as the **2-character skeleton** but each panel shows TWO people standing
close together. Label reads "[NAME] & [NAME]". Keep both couples' framing equal.

---

## FILLING TIPS (so prompts never feel generic)
- **Person description:** use `06-ROYAL-CHARACTER-BANK.md` for accurate hair,
  age, signature look. Be specific (e.g. "auburn hair in an updo", "blonde
  bouffant", "greying short beard").
- **Outfit:** name the garment + colour + material + accessories (hat, brooch,
  pearls, sash, medals, gloves). Keep outfits in the SAME family across panels.
- **Pose:** standing hands-clasped, seated legs-crossed, walking candid, couple
  pose. Use the SAME pose for every panel of one poster.
- **Expression:** warm smile, gentle smile, composed/dignified, joyful.
- **Scene:** one concrete setting kept consistent across panels (same palace
  room / same garden / same studio), varying only small details.
- **Always keep** the crop-safe block + realism/avoid line exactly as written.
