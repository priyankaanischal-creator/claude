"""
instructor_parser.py
--------------------
Parses a beat-by-beat "visual instructor" file into scene specs with precise
clip + image search queries. NO LLM / API needed - the visual instructions
already contain the analysis; we just translate them into search queries.

Expected beat format (labels are matched loosely / case-insensitively):

    SECTION HEADER (optional, all-caps line)
    Script Cue (narration): "..."
    Visual / Exact Clip to Use: ...
    On-Screen Text: ...
    Editor Notes: ...

For every beat we extract:
  - the narration line
  - the visual description (the source of the queries)
  - the on-screen text + editor notes (saved for the editor, not searched)

Query building (heuristic, ordered most-specific first):
  1. ALL-CAPS scene names in the visual  -> "{subject} {scene name} scene"
  2. quoted famous lines                 -> "{subject} {line} scene"
  3. named entities (people/places)       -> anchored or standalone
  4. fallback: subject + salient nouns
Beats explicitly marked non-film (e.g. "NOT Scarface", "archival", "abstract")
are searched WITHOUT the film anchor so we get real-world / stock footage.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field, asdict
from typing import List, Optional

# --- label patterns --------------------------------------------------------

_LABELS = {
    "narration": re.compile(r"^\s*Script Cue\s*\(narration\)\s*:\s*(.*)$", re.I),
    "visual": re.compile(r"^\s*Visual\s*/?\s*Exact Clip to Use\s*:\s*(.*)$", re.I),
    "onscreen": re.compile(r"^\s*On-?Screen Text\s*:\s*(.*)$", re.I),
    "notes": re.compile(r"^\s*Editor Notes\s*:\s*(.*)$", re.I),
}

# words that look like proper nouns only because they start a sentence
_INITIAL_NOISE = {
    "Quick", "Then", "Continue", "Hold", "Hard", "Show", "Brief", "Slow",
    "Final", "Optional", "Photo", "Archival", "Split", "Abstract", "End",
    "Or", "And", "The", "A", "An", "Let", "Establish", "Focus", "Build",
    "These", "This", "That", "Two", "Same", "Keep", "Pull", "Cut", "Close",
    "Documentary", "Stock", "Still", "Text", "Tony",  # Tony handled via subject anchor
    "His", "He", "She", "Her", "Him", "Its", "Their", "Your", "They", "We",
    "You", "When", "Where", "While", "After", "Before", "Most", "Here",
    "There", "Then", "Now", "But", "Not", "Brief", "Insert", "Continue",
}

# markers that mean "do NOT use the film as the source"
_NONFILM_MARKERS = (
    "not scarface", "non-film", "archival", "stock shot", "stock footage",
    "real-world", "documentary", "abstract", "universal", "newspaper",
    "rap album", "music video", "end card", "skyline", "establishing shot",
    "text card", "mpaa",
)


@dataclass
class Beat:
    index: int
    section: str
    narration: str
    visual: str
    on_screen: str = ""
    notes: str = ""
    is_film: bool = True
    image_queries: List[str] = field(default_factory=list)
    clip_queries: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


# --- low-level parsing ------------------------------------------------------

def _looks_like_section(line: str) -> bool:
    s = line.strip()
    if not s or any(p.match(line) for p in _LABELS.values()):
        return False
    if s[0].isdigit():  # e.g. "1.  Visual Direction (Beat-by-Beat)"
        return False
    if any(ch in s for ch in ".·:()\""):  # section headers are bare labels
        return False
    letters = [c for c in s if c.isalpha()]
    if not letters:
        return False
    upper_ratio = sum(c.isupper() for c in letters) / len(letters)
    return upper_ratio > 0.8 and len(s) < 48


def parse_beats(text: str) -> List[Beat]:
    lines = text.splitlines()
    beats: List[Beat] = []
    section = ""
    cur: Optional[dict] = None
    field_name: Optional[str] = None

    def flush():
        nonlocal cur
        if cur and (cur["narration"] or cur["visual"]):
            beats.append(Beat(
                index=len(beats) + 1,
                section=cur["section"],
                narration=cur["narration"].strip(),
                visual=cur["visual"].strip(),
                on_screen=cur["onscreen"].strip(),
                notes=cur["notes"].strip(),
            ))
        cur = None

    for line in lines:
        matched_label = None
        for name, pat in _LABELS.items():
            m = pat.match(line)
            if m:
                matched_label = name
                inline = m.group(1)
                if name == "narration":
                    flush()  # a new narration line starts a new beat
                    cur = {"section": section, "narration": "", "visual": "",
                           "onscreen": "", "notes": ""}
                if cur is None:
                    cur = {"section": section, "narration": "", "visual": "",
                           "onscreen": "", "notes": ""}
                cur[name] += (" " + inline if cur[name] else inline)
                field_name = name
                break

        if matched_label:
            continue

        # A section header can appear between beats (while the previous beat is
        # still held in `cur`). Detect it first so it never pollutes a field.
        if _looks_like_section(line):
            section = line.strip()
            field_name = None
            continue

        if cur is None:
            continue

        if field_name and line.strip():
            cur[field_name] += " " + line.strip()

    flush()
    return beats


# --- query extraction -------------------------------------------------------

# Quotes: straight/curly DOUBLE quotes, and curly SINGLE pairs only.
# We deliberately exclude the straight apostrophe so "It's" / "Tony's" are safe,
# and curly ’ alone won't match (needs an opening ‘).
_DOUBLE_RE = re.compile(r"[\"“]([^\"”]{3,70}?)[\"”]")
_CURLY_SINGLE_RE = re.compile(r"‘([^’]{3,70}?)’")
_CAPS_RE = re.compile(r"\b([A-Z][A-Z0-9'\-]+(?:\s+[A-Z0-9'\-&]+){1,6})\b")
_PROPER_RE = re.compile(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b")

_LEADING_ARTICLE = re.compile(r"^(THE|A|AN)\s+", re.I)


def _polish_query(s: str) -> str:
    """Trim a query: cut at ellipsis, drop colon/dash tails, cap length."""
    s = s.strip()
    # cut everything from the first ellipsis
    s = re.split(r"…|\.\.\.", s)[0]
    # drop a trailing 'scene' label temporarily to manage length
    had_scene = s.endswith(" scene")
    core = s[:-6] if had_scene else s
    # remove colon segments / stray punctuation
    core = core.split(":")[0]
    core = core.replace("—", " ").replace(">", " ").replace('"', " ")
    core = re.sub(r"\s+", " ", core).strip(" ,;-")
    # cap to 10 words to keep searches focused
    words = core.split()
    if len(words) > 10:
        core = " ".join(words[:10])
    if not core:
        return ""
    return f"{core} scene" if had_scene else core


def _clean_quote(q: str) -> Optional[str]:
    q = q.strip().strip("….,;:!- ").strip()
    if len(q.split()) < 2:
        return None
    return q.lower() if q.isupper() else q


def _quotes(text: str, allow_double: bool) -> List[str]:
    found = list(_CURLY_SINGLE_RE.findall(text))
    if allow_double:
        found += list(_DOUBLE_RE.findall(text))
    out = []
    for q in found:
        c = _clean_quote(q)
        if c:
            out.append(c)
    seen, res = set(), []
    for q in out:
        if q.lower() not in seen:
            seen.add(q.lower())
            res.append(q)
    return res


def _caps_scene_names(text: str) -> List[str]:
    # drop parentheticals and quote chars first so "(Scarface)" / quotes don't leak
    text = re.sub(r"\([^)]*\)", " ", text)
    text = re.sub(r"[\"“”]", " ", text)
    names = []
    for c in _CAPS_RE.findall(text):
        phrase = _LEADING_ARTICLE.sub("", c).strip()  # only strip a leading article
        words = phrase.split()
        if len(words) >= 2 and not phrase.isdigit():
            names.append(phrase.title())
    seen, res = set(), []
    for n in names:
        if n.lower() not in seen:
            seen.add(n.lower())
            res.append(n)
    return res


def _proper_nouns(text: str) -> List[str]:
    # strip parentheticals to reduce noise like "(Scarface)"
    text = re.sub(r"\([^)]*\)", " ", text)
    out = []
    for p in _PROPER_RE.findall(text):
        words = p.split()
        # drop if the whole phrase is just sentence-initial noise
        if all(w in _INITIAL_NOISE for w in words):
            continue
        # drop a single noise word
        if len(words) == 1 and words[0] in _INITIAL_NOISE:
            continue
        out.append(p)
    seen, res = set(), []
    for p in out:
        if p.lower() not in seen:
            seen.add(p.lower())
            res.append(p)
    return res


def build_queries(beat: Beat, subject: str, max_q: int = 3) -> None:
    """Populate beat.image_queries and beat.clip_queries from its visual text."""
    visual = beat.visual
    blob = f"{beat.narration} {beat.visual}"
    low = blob.lower()
    beat.is_film = not any(mk in low for mk in _NONFILM_MARKERS)

    scenes = _caps_scene_names(visual)
    # famous lines: double-quotes only from VISUAL (narration is fully quoted),
    # plus curly-single famous lines from both narration and visual.
    raw_quotes = _quotes(visual, allow_double=True) + _quotes(beat.narration, allow_double=False)
    _seen = set()
    quotes = []
    for q in raw_quotes:
        if q.lower() not in _seen:
            _seen.add(q.lower())
            quotes.append(q)
    propers = _proper_nouns(visual)

    anchor = subject if beat.is_film else ""

    def q(*parts):
        s = " ".join(p for p in parts if p).strip()
        s = re.sub(r"\s+", " ", s)
        return s

    clip_q: List[str] = []
    img_q: List[str] = []

    # 1) explicit CAPS scene names (strongest signal)
    for name in scenes[:2]:
        clip_q.append(q(anchor, name, "scene"))
        img_q.append(q(anchor, name, "still"))

    # 2) famous quoted lines
    for line in quotes[:2]:
        clip_q.append(q(anchor, line, "scene"))
        img_q.append(q(anchor, line))

    # 3) named entities (people / places) - good for both film + non-film beats
    if propers:
        if beat.is_film:
            # combine subject with the first couple of distinctive names
            top = [p for p in propers if p.lower() not in ("tony", "scarface")][:2]
            for p in top:
                clip_q.append(q(anchor, p, "scene"))
                img_q.append(q(anchor, p))
        else:
            # non-film: search the entities/topic directly (archival/stock/etc.)
            joined = " ".join(propers[:3])
            clip_q.append(q(joined, "archival footage"))
            img_q.append(q(joined))
            img_q.append(q(propers[0]) if propers else "")

    # 4) fallback if nothing extracted
    if not clip_q:
        clip_q.append(q(anchor or subject, "scene"))
    if not img_q:
        img_q.append(q(anchor or subject))

    def dedup(seq):
        seen, res = set(), []
        for s in seq:
            s = _polish_query(s)
            if s and s.lower() not in seen:
                seen.add(s.lower())
                res.append(s)
        return res[:max_q]

    beat.clip_queries = dedup(clip_q)
    beat.image_queries = dedup(img_q)


def parse_instructor(path: str, subject: str, max_q: int = 3) -> List[Beat]:
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    beats = parse_beats(text)
    for b in beats:
        build_queries(b, subject, max_q=max_q)
    return beats


if __name__ == "__main__":
    import sys
    p = sys.argv[1] if len(sys.argv) > 1 else "scripts/tony_montana_visual_instructor.txt"
    subj = sys.argv[2] if len(sys.argv) > 2 else "Scarface 1983 Tony Montana"
    beats = parse_instructor(p, subj)
    print(f"Parsed {len(beats)} beats\n")
    for b in beats:
        tag = "FILM" if b.is_film else "EXTERNAL"
        print(f"[{b.index:02d}] ({b.section}) [{tag}]")
        print(f"     narr : {b.narration[:70]}")
        print(f"     CLIP : {b.clip_queries}")
        print(f"     IMG  : {b.image_queries}")
        print()
