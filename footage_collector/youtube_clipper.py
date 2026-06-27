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
import tempfile
from dataclasses import dataclass, asdict
from typing import List, Optional


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

def search_videos(query: str, limit: int = 5, max_minutes: int = 40,
                  auth: YtAuth = DEFAULT_AUTH) -> List[dict]:
    """
    Return a list of candidate videos: [{id, title, duration}, ...].
    Uses yt-dlp's ytsearch (no API key). Filters out absurdly long videos.
    """
    cmd = [
        "yt-dlp",
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
        results.append({"id": vid, "title": title, "duration": dur})
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
    cmd = [
        "yt-dlp", url,
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
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "json", path,
    ]
    try:
        proc = _run(cmd, timeout=30)
        data = json.loads(proc.stdout or "{}")
        return float(data.get("format", {}).get("duration", 0.0))
    except Exception:
        return 0.0


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
) -> bool:
    """Download just [start, start+duration] of the video and normalise to 16:9 mp4."""
    url = f"https://www.youtube.com/watch?v={video_id}"
    end = start + duration
    workdir = tempfile.mkdtemp(prefix="ytclip_")
    raw_tmpl = os.path.join(workdir, "raw.%(ext)s")
    section = f"*{start:.2f}-{end:.2f}"
    cmd = [
        "yt-dlp", url,
        "--download-sections", section,
        "--force-keyframes-at-cuts",
        "-f", f"bv*[height<={max_height}]+ba/b[height<={max_height}]/b",
        "--merge-output-format", "mp4",
        "--no-warnings", "--quiet",
        "-o", raw_tmpl,
    ] + auth.args()
    try:
        proc = _run(cmd, timeout=300)
    except subprocess.TimeoutExpired:
        shutil.rmtree(workdir, ignore_errors=True)
        return False

    raw = None
    for fn in os.listdir(workdir):
        if fn.startswith("raw"):
            raw = os.path.join(workdir, fn)
            break
    if not raw or os.path.getsize(raw) == 0:
        shutil.rmtree(workdir, ignore_errors=True)
        return False

    # Re-trim to exact duration, normalise to a clean 16:9 1080p mp4 so every
    # clip drops straight onto a landscape timeline without resizing.
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    ff = ["ffmpeg", "-y", "-i", raw, "-t", f"{duration:.2f}"]
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
        _run(ff, timeout=180)
    except subprocess.TimeoutExpired:
        shutil.rmtree(workdir, ignore_errors=True)
        return False

    shutil.rmtree(workdir, ignore_errors=True)
    return os.path.exists(out_path) and os.path.getsize(out_path) > 0


# --- top-level orchestration ----------------------------------------------

PRE_ROLL = 1.0  # start the clip ~1s before the matched line for action context


def collect_clip(
    query: str,
    keywords: List[str],
    out_path: str,
    duration: float = 5.0,
    search_n: int = 6,
    max_height: int = 720,
    auth: YtAuth = DEFAULT_AUTH,
    exclude_ids: Optional[set] = None,
) -> Optional[ClipResult]:
    """
    Full pipeline for one scene clip:
      1. search YouTube for candidate videos
      2. read each candidate's subtitles and score how well it contains the
         scene's keywords (so we pick the video that ACTUALLY has the moment)
      3. download a short window centred on the best-matching line
      4. normalise to a clean 16:9 1080p mp4

    `exclude_ids` lets the caller avoid reusing the same video for multiple
    clips in the same scene.
    """
    exclude_ids = exclude_ids or set()
    candidates = search_videos(query, limit=search_n, auth=auth)
    candidates = [c for c in candidates if c["id"] not in exclude_ids]
    if not candidates:
        return None

    workdir = tempfile.mkdtemp(prefix="ytsubs_")
    try:
        # Score every candidate by subtitle keyword match.
        scored = []
        for cand in candidates:
            vid = cand["id"]
            vdur = cand["duration"] or 0.0
            ts = best_timestamp(vid, keywords, duration, workdir, auth)
            if ts is not None:
                m_start, matched, score = ts
            else:
                m_start, matched, score = None, "", 0
            scored.append((score, cand, vdur, m_start, matched))

        # Best matches first; tie-break toward shorter (more focused) videos.
        scored.sort(key=lambda x: (x[0], -(x[2] or 1e9)), reverse=True)

        for score, cand, vdur, m_start, matched in scored:
            vid = cand["id"]
            if m_start is not None and score > 0:
                start = max(0.0, m_start - PRE_ROLL)  # begin just before the line
            else:
                start = max(5.0, vdur * 0.2) if vdur else 30.0  # fallback slice

            if vdur and start + duration > vdur:
                start = max(0.0, vdur - duration - 1)

            ok = download_section(vid, start, duration, out_path, max_height, auth)
            if ok:
                return ClipResult(
                    path=out_path,
                    video_id=vid,
                    url=f"https://www.youtube.com/watch?v={vid}",
                    title=cand["title"],
                    start=round(start, 2),
                    duration=duration,
                    matched_text=matched,
                    match_score=score,
                )
        return None
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


if __name__ == "__main__":
    import sys
    q = sys.argv[1] if len(sys.argv) > 1 else "Scarface Tony Montana say hello to my little friend"
    print("Searching:", q)
    cands = search_videos(q, limit=3)
    for c in cands:
        print(" ", c)
    if cands:
        res = collect_clip(
            q,
            keywords=["hello", "little", "friend"],
            out_path="/tmp/test_clip/clip.mp4",
            duration=6.0,
            search_n=3,
        )
        print("RESULT:", res)
