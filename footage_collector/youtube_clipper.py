"""
youtube_clipper.py
------------------
Keyless YouTube footage sourcing using yt-dlp + ffmpeg.

For a given search query it:
  1. searches YouTube (ytsearch, no API key),
  2. tries to locate the most relevant moment inside a candidate video by
     scanning its auto-generated subtitles for the scene's keywords,
  3. downloads only that ~N-second section and trims it to exact length.

Everything is best-effort with graceful fallbacks: if subtitles are missing
or no keyword matches, it falls back to a sensible offset into the video.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, asdict
from typing import List, Optional

_HERE = os.path.dirname(os.path.abspath(__file__))
_BIN = os.path.join(_HERE, "bin")

# Call yt-dlp as a module of THIS Python interpreter. This works even when the
# `yt-dlp` command isn't on the system PATH (common on Windows after pip install).
_YTDLP = [sys.executable, "-m", "yt_dlp"]


def _exe(name: str) -> str:
    """Resolve ffmpeg/ffprobe: prefer a bundled ./bin copy, else system PATH."""
    for cand in (os.path.join(_BIN, name), os.path.join(_BIN, name + ".exe")):
        if os.path.isfile(cand):
            return cand
    return shutil.which(name) or shutil.which(name + ".exe") or name


def _ffmpeg_location_args() -> List[str]:
    """Tell yt-dlp where ffmpeg is, if we have a bundled copy."""
    if os.path.isdir(_BIN) and (os.path.isfile(os.path.join(_BIN, "ffmpeg"))
                                or os.path.isfile(os.path.join(_BIN, "ffmpeg.exe"))):
        return ["--ffmpeg-location", _BIN]
    return []


@dataclass
class ClipResult:
    path: str
    video_id: str
    url: str
    title: str
    start: float
    duration: float
    matched_text: str
    match_score: int

    def to_dict(self) -> dict:
        return asdict(self)


def _run(cmd: List[str], timeout: int = 180) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=timeout,
    )


# --- authentication / anti-bot args ----------------------------------------
# YouTube blocks downloads from datacenter / unknown IPs with a
# "Sign in to confirm you're not a bot" error. On a normal machine where the
# user is logged into YouTube in their browser, passing cookies fixes this.

@dataclass
class YtAuth:
    cookies_file: Optional[str] = None          # path to a cookies.txt
    cookies_from_browser: Optional[str] = None  # e.g. "chrome", "firefox", "edge"
    player_client: Optional[str] = None         # e.g. "android", "web"

    def args(self) -> List[str]:
        out: List[str] = []
        if self.cookies_file:
            out += ["--cookies", self.cookies_file]
        if self.cookies_from_browser:
            out += ["--cookies-from-browser", self.cookies_from_browser]
        if self.player_client:
            out += ["--extractor-args", f"youtube:player_client={self.player_client}"]
        return out


DEFAULT_AUTH = YtAuth()


# --- search ----------------------------------------------------------------

# Titles that usually mean commentary/analysis (NOT actual movie footage).
_JUNK_TITLE = (
    "explained", "breakdown", "reaction", "react", "review", "analysis",
    "analy", "theory", "theories", "ranked", "ranking", "essay", "easter egg",
    "things you missed", "things you didnt", "facts", "top 10", "top ten",
    "retrospective", "podcast", "commentary", "explain", "iceberg",
    "why ", "how ", "vs ", "tier list", "deep dive", "recap", "summary",
    "discussion", "interview",
)
# Titles that usually ARE real movie footage.
_GOOD_TITLE = (
    "movie clip", "movie scene", "official clip", "scene", "clip", " hd",
    "4k", "remaster", "blu-ray", "bluray", "full scene",
)


def _title_score(title: str, duration: float) -> int:
    """Heuristic: positive = looks like real movie footage, negative = commentary."""
    t = " " + title.lower() + " "
    score = 0
    for kw in _JUNK_TITLE:
        if kw in t:
            score -= 4
    for kw in _GOOD_TITLE:
        if kw in t:
            score += 3
    # short clips are usually the actual scene; long videos are usually essays
    if duration:
        if duration <= 240:
            score += 2
        elif duration > 900:
            score -= 4
        elif duration > 480:
            score -= 2
    return score


def search_videos(query: str, limit: int = 8, max_minutes: int = 30,
                  auth: YtAuth = DEFAULT_AUTH) -> List[dict]:
    """
    Return candidate videos [{id, title, duration, title_score}, ...], best
    (most footage-like) first. Uses yt-dlp ytsearch (no API key).
    """
    cmd = _YTDLP + [
        f"ytsearch{limit}:{query}",
        "--flat-playlist",
        "--no-warnings",
        "--quiet",
        "--print", "%(id)s\t%(title)s\t%(duration)s",
    ] + auth.args()
    try:
        proc = _run(cmd, timeout=90)
    except subprocess.TimeoutExpired:
        return []
    results: List[dict] = []
    for line in proc.stdout.strip().splitlines():
        parts = line.split("\t")
        if len(parts) < 1 or not parts[0]:
            continue
        vid = parts[0].strip()
        title = parts[1].strip() if len(parts) > 1 else ""
        dur_raw = parts[2].strip() if len(parts) > 2 else ""
        try:
            dur = float(dur_raw)
        except ValueError:
            dur = 0.0
        if max_minutes and dur and dur > max_minutes * 60:
            continue
        results.append({
            "id": vid, "title": title, "duration": dur,
            "title_score": _title_score(title, dur),
        })
    # Best-looking footage first.
    results.sort(key=lambda r: r["title_score"], reverse=True)
    return results


# --- subtitle based timestamp matching -------------------------------------

_TS_RE = re.compile(
    r"(\d{2}):(\d{2}):(\d{2})[.,](\d{3})\s*-->\s*(\d{2}):(\d{2}):(\d{2})[.,](\d{3})"
)


def _ts_to_sec(h: str, m: str, s: str, ms: str) -> float:
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000.0


def _parse_vtt(path: str) -> List[tuple]:
    """Parse a .vtt/.srt file into [(start_sec, end_sec, text), ...]."""
    cues: List[tuple] = []
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except OSError:
        return cues

    blocks = re.split(r"\n\s*\n", content)
    for block in blocks:
        m = _TS_RE.search(block)
        if not m:
            continue
        start = _ts_to_sec(*m.group(1, 2, 3, 4))
        end = _ts_to_sec(*m.group(5, 6, 7, 8))
        # text = everything after the timestamp line
        lines = block.splitlines()
        text_lines = []
        seen_ts = False
        for ln in lines:
            if _TS_RE.search(ln):
                seen_ts = True
                continue
            if seen_ts:
                # strip vtt inline tags like <00:00:01.000><c> ... </c>
                clean = re.sub(r"<[^>]+>", "", ln).strip()
                if clean:
                    text_lines.append(clean)
        text = " ".join(text_lines)
        if text:
            cues.append((start, end, text))
    return cues


def _fetch_subtitles(video_id: str, workdir: str, auth: YtAuth = DEFAULT_AUTH) -> Optional[str]:
    """Download auto/manual English subs (vtt) without the video. Returns path."""
    url = f"https://www.youtube.com/watch?v={video_id}"
    out_tmpl = os.path.join(workdir, "%(id)s.%(ext)s")
    cmd = _YTDLP + [
        url,
        "--skip-download",
        "--write-subs", "--write-auto-subs",
        "--sub-langs", "en.*,en",
        "--sub-format", "vtt/srt/best",
        "--no-warnings", "--quiet",
        "-o", out_tmpl,
    ] + auth.args()
    try:
        _run(cmd, timeout=90)
    except subprocess.TimeoutExpired:
        return None
    for fn in os.listdir(workdir):
        if fn.startswith(video_id) and (fn.endswith(".vtt") or fn.endswith(".srt")):
            return os.path.join(workdir, fn)
    return None


def best_timestamp(
    video_id: str,
    keywords: List[str],
    duration: float,
    workdir: str,
    auth: YtAuth = DEFAULT_AUTH,
) -> Optional[tuple]:
    """
    Find the start time (seconds) of the best-matching subtitle window for the
    given keywords. Returns (start_sec, matched_text, score) or None.
    """
    sub_path = _fetch_subtitles(video_id, workdir, auth)
    if not sub_path:
        return None
    cues = _parse_vtt(sub_path)
    if not cues:
        return None

    kw = [k.lower() for k in keywords if len(k) >= 4]
    if not kw:
        return None

    best = None  # (score, start, text)
    for (start, end, text) in cues:
        low = text.lower()
        score = sum(1 for k in kw if k in low)
        if score == 0:
            continue
        # prefer cues whose window roughly fits our clip length
        if best is None or score > best[0]:
            best = (score, start, text)

    if best is None:
        return None
    return (max(0.0, best[1]), best[2], best[0])


# --- download + trim -------------------------------------------------------

def _ffprobe_duration(path: str) -> float:
    cmd = [
        _exe("ffprobe"), "-v", "error", "-show_entries", "format=duration",
        "-of", "json", path,
    ]
    try:
        proc = _run(cmd, timeout=30)
        data = json.loads(proc.stdout or "{}")
        return float(data.get("format", {}).get("duration", 0.0))
    except Exception:
        return 0.0


def _err_reason(proc) -> str:
    """Pull a short, human-readable failure reason out of yt-dlp output."""
    text = (getattr(proc, "stderr", "") or "") + "\n" + (getattr(proc, "stdout", "") or "")
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    for ln in reversed(lines):
        if "ERROR" in ln or "error" in ln.lower():
            return ln[:220]
    return (lines[-1][:220] if lines else "unknown error")


def check_tools() -> dict:
    """Verify yt-dlp and ffmpeg are usable; used for a startup preflight line."""
    info = {}
    try:
        p = _run(_YTDLP + ["--version"], timeout=60)
        info["yt_dlp"] = p.stdout.strip() if p.returncode == 0 else "MISSING (pip install yt-dlp)"
    except Exception:
        info["yt_dlp"] = "MISSING (pip install yt-dlp)"
    ff = _exe("ffmpeg")
    try:
        p = _run([ff, "-version"], timeout=30)
        info["ffmpeg"] = (ff if p.returncode == 0 else "MISSING")
    except Exception:
        info["ffmpeg"] = "MISSING"
    return info


def download_section(
    video_id: str,
    start: float,
    duration: float,
    out_path: str,
    max_height: int = 720,
    auth: YtAuth = DEFAULT_AUTH,
    normalize_169: bool = True,
    target_w: int = 1920,
    target_h: int = 1080,
) -> tuple:
    """Download [start, start+duration] and normalise to 16:9 mp4.
    Returns (ok: bool, reason: str)."""
    url = f"https://www.youtube.com/watch?v={video_id}"
    end = start + duration
    workdir = tempfile.mkdtemp(prefix="ytclip_")
    raw_tmpl = os.path.join(workdir, "raw.%(ext)s")
    section = f"*{start:.2f}-{end:.2f}"

    # Try several format selectors. YouTube + an out-of-date yt-dlp often throws
    # "Requested format is not available"; falling back to plain best usually works.
    fmt_candidates = [
        f"bv*[height<={max_height}]+ba/b[height<={max_height}]",
        "bv*+ba/b",
        "b",
        "best",
    ]

    proc = None
    raw = None
    last_reason = "download failed"
    for fmt in fmt_candidates:
        for fn in os.listdir(workdir):           # clear any partial leftovers
            try:
                os.remove(os.path.join(workdir, fn))
            except OSError:
                pass
        cmd = _YTDLP + [
            url,
            "--download-sections", section,
            "--force-keyframes-at-cuts",
            "-f", fmt,
            "--merge-output-format", "mp4",
            "--no-warnings",
            "-o", raw_tmpl,
        ] + _ffmpeg_location_args() + auth.args()
        try:
            proc = _run(cmd, timeout=300)
        except subprocess.TimeoutExpired:
            shutil.rmtree(workdir, ignore_errors=True)
            return False, "yt-dlp timed out"

        raw = None
        for fn in os.listdir(workdir):
            if fn.startswith("raw"):
                raw = os.path.join(workdir, fn)
                break
        if raw and os.path.getsize(raw) > 0:
            break  # got it
        last_reason = _err_reason(proc)
        # only worth trying other formats for format errors; otherwise stop early
        if "format is not available" not in last_reason.lower():
            break

    if not raw or os.path.getsize(raw) == 0:
        shutil.rmtree(workdir, ignore_errors=True)
        return False, last_reason

    # Re-trim to exact duration, normalise to a clean 16:9 1080p mp4.
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    ff = [_exe("ffmpeg"), "-y", "-i", raw, "-t", f"{duration:.2f}"]
    if normalize_169:
        vf = (
            f"scale={target_w}:{target_h}:force_original_aspect_ratio=decrease,"
            f"pad={target_w}:{target_h}:(ow-iw)/2:(oh-ih)/2:black,setsar=1,fps=30"
        )
        ff += ["-vf", vf]
    ff += [
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
        "-c:a", "aac", "-b:a", "128k",
        "-movflags", "+faststart",
        out_path,
    ]
    try:
        ffproc = _run(ff, timeout=180)
    except subprocess.TimeoutExpired:
        shutil.rmtree(workdir, ignore_errors=True)
        return False, "ffmpeg timed out"

    shutil.rmtree(workdir, ignore_errors=True)
    if os.path.exists(out_path) and os.path.getsize(out_path) > 0:
        return True, ""
    return False, _err_reason(ffproc) or "ffmpeg produced no output"


# --- top-level orchestration ----------------------------------------------

PRE_ROLL = 1.0  # start the clip ~1s before the matched line for action context


def collect_clip(
    query: str,
    keywords: List[str],
    out_path: str,
    duration: float = 5.0,
    search_n: int = 8,
    max_height: int = 720,
    auth: YtAuth = DEFAULT_AUTH,
    exclude_ids: Optional[set] = None,
    used_sections: Optional[set] = None,
) -> tuple:
    """
    Full pipeline for one scene clip:
      1. search YouTube and rank candidates by how much they look like real
         movie footage (title) rather than commentary/reaction/essay videos
      2. read each candidate's subtitles and score keyword match (so we pick the
         video + timestamp that ACTUALLY has the moment)
      3. download a short window centred on the best-matching line
      4. normalise to a clean 16:9 1080p mp4

    `exclude_ids`    : video ids to skip entirely (global de-dup).
    `used_sections`  : set of "videoid@bucket" already used anywhere, so the
                       SAME clip section never repeats across scenes.
    Returns (ClipResult | None, reason).
    """
    exclude_ids = exclude_ids or set()
    used_sections = used_sections if used_sections is not None else set()
    candidates = search_videos(query, limit=search_n, auth=auth)
    candidates = [c for c in candidates if c["id"] not in exclude_ids]
    if not candidates:
        return None, "no YouTube search results"

    last_reason = "download failed"
    workdir = tempfile.mkdtemp(prefix="ytsubs_")
    try:
        # Score candidates: subtitle keyword match (x3) + footage-like title.
        scored = []
        for cand in candidates:
            vid = cand["id"]
            vdur = cand["duration"] or 0.0
            ts = best_timestamp(vid, keywords, duration, workdir, auth)
            if ts is not None:
                m_start, matched, kscore = ts
            else:
                m_start, matched, kscore = None, "", 0
            combined = kscore * 3 + cand.get("title_score", 0)
            scored.append((combined, kscore, cand, vdur, m_start, matched))

        scored.sort(key=lambda x: (x[0], -(x[3] or 1e9)), reverse=True)

        for combined, kscore, cand, vdur, m_start, matched in scored:
            vid = cand["id"]
            if m_start is not None and kscore > 0:
                start = max(0.0, m_start - PRE_ROLL)
            else:
                start = max(5.0, vdur * 0.2) if vdur else 30.0

            if vdur and start + duration > vdur:
                start = max(0.0, vdur - duration - 1)

            # Skip a section that was already used elsewhere (no repeats).
            bucket = f"{vid}@{int(start // 3)}"
            if bucket in used_sections:
                continue

            ok, reason = download_section(vid, start, duration, out_path, max_height, auth)
            if ok:
                used_sections.add(bucket)
                return ClipResult(
                    path=out_path,
                    video_id=vid,
                    url=f"https://www.youtube.com/watch?v={vid}",
                    title=cand["title"],
                    start=round(start, 2),
                    duration=duration,
                    matched_text=matched,
                    match_score=kscore,
                ), ""
            last_reason = reason or last_reason
        return None, last_reason
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


def extract_frames(clip_path: str, n: int, out_dir: str, prefix: str = "frame") -> List[str]:
    """Grab N evenly-spaced still frames from a clip (on-point images straight
    from the matching footage). Returns list of saved image paths."""
    if n <= 0 or not os.path.isfile(clip_path):
        return []
    dur = _ffprobe_duration(clip_path) or 5.0
    os.makedirs(out_dir, exist_ok=True)
    paths: List[str] = []
    for i in range(n):
        frac = (i + 1) / (n + 1)
        t = max(0.1, dur * frac)
        outp = os.path.join(out_dir, f"{prefix}_{i + 1:02d}.jpg")
        cmd = [_exe("ffmpeg"), "-y", "-ss", f"{t:.2f}", "-i", clip_path,
               "-frames:v", "1", "-q:v", "2", outp]
        try:
            _run(cmd, timeout=60)
        except subprocess.TimeoutExpired:
            continue
        if os.path.exists(outp) and os.path.getsize(outp) > 0:
            paths.append(outp)
    return paths


if __name__ == "__main__":
    import sys
    q = sys.argv[1] if len(sys.argv) > 1 else "Scarface Tony Montana say hello to my little friend"
    print("Searching:", q)
    cands = search_videos(q, limit=3)
    for c in cands:
        print(" ", c)
    if cands:
        res, reason = collect_clip(
            q,
            keywords=["hello", "little", "friend"],
            out_path="/tmp/test_clip/clip.mp4",
            duration=6.0,
            search_n=3,
        )
        print("RESULT:", res)
        print("REASON:", reason)
