"""
image_collector.py
------------------
Keyless image sourcing using DuckDuckGo image search (ddgs library).

Quality focused for 16:9 video:
  - asks DuckDuckGo for Large / Wallpaper, Wide-layout images
  - filters to LANDSCAPE, high-resolution images (min width, sane aspect ratio)
  - ranks candidates by resolution + closeness to 16:9 (1.78)
  - accepts MULTIPLE queries per scene and de-duplicates results

De-duplication (NEW):
  A shared DedupState can be passed across ALL scenes so the SAME image never
  lands in two different scene folders. It detects duplicates three ways:
    1. same source URL
    2. same exact bytes (md5)
    3. visually near-identical images at different sizes (perceptual aHash)
"""

from __future__ import annotations

import hashlib
import io
import os
import time
import warnings
from dataclasses import dataclass, asdict, field
from typing import List, Optional, Set, Union
from urllib.parse import urlparse

import requests

# Quieten a harmless Pillow warning about palette images with transparency.
warnings.filterwarnings("ignore", message=".*Palette images with Transparency.*")

try:
    from ddgs import DDGS
except ImportError:  # older package name
    from duckduckgo_search import DDGS  # type: ignore

try:
    from PIL import Image
    _HAVE_PIL = True
except ImportError:
    _HAVE_PIL = False


_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}

_VALID_CT = ("image/jpeg", "image/jpg", "image/png", "image/webp")
_EXT = {"image/jpeg": ".jpg", "image/jpg": ".jpg", "image/png": ".png", "image/webp": ".webp"}

TARGET_AR = 16 / 9  # 1.778
PHASH_MAX_DISTANCE = 6  # Hamming distance under which images are "the same"


# --- global de-duplication state -------------------------------------------

@dataclass
class DedupState:
    """Shared across all scenes to prevent the same image appearing twice."""
    urls: Set[str] = field(default_factory=set)
    md5s: Set[str] = field(default_factory=set)
    phashes: List[int] = field(default_factory=list)

    def url_seen(self, url: str) -> bool:
        return _dedup_key(url) in self.urls

    def add_url(self, url: str) -> None:
        self.urls.add(_dedup_key(url))

    def is_dup_bytes(self, data: bytes) -> bool:
        md5 = hashlib.md5(data).hexdigest()
        if md5 in self.md5s:
            return True
        ph = _average_hash(data)
        if ph is not None:
            for seen in self.phashes:
                if _hamming(ph, seen) <= PHASH_MAX_DISTANCE:
                    return True
        # not a dup -> record
        self.md5s.add(md5)
        if ph is not None:
            self.phashes.append(ph)
        return False


def _average_hash(data: bytes, size: int = 8) -> Optional[int]:
    """Perceptual average-hash; returns an int bitmask or None if PIL missing."""
    if not _HAVE_PIL:
        return None
    try:
        im = Image.open(io.BytesIO(data)).convert("L").resize((size, size))
        pixels = list(im.getdata())
        avg = sum(pixels) / len(pixels)
        bits = 0
        for i, p in enumerate(pixels):
            if p >= avg:
                bits |= (1 << i)
        return bits
    except Exception:
        return None


def _hamming(a: int, b: int) -> int:
    return bin(a ^ b).count("1")


@dataclass
class ImageResult:
    path: str
    source_url: str
    query: str = ""
    width: Optional[int] = None
    height: Optional[int] = None

    def to_dict(self) -> dict:
        return asdict(self)


def _aspect_ok(w: int, h: int, min_ar: float, max_ar: float) -> bool:
    if not w or not h:
        return False
    ar = w / h
    return min_ar <= ar <= max_ar


def _score(w: int, h: int) -> float:
    if not w or not h:
        return 0.0
    ar = w / h
    ar_penalty = abs(ar - TARGET_AR) * 1000
    res_bonus = min(w, 3840)
    return res_bonus - ar_penalty


def _dedup_key(url: str) -> str:
    p = urlparse(url)
    return (p.netloc + p.path).lower()


def _ddgs_images(query: str, max_results: int, size: str):
    """Run one DuckDuckGo image search with a timeout + one retry."""
    last_exc = None
    for attempt in range(2):
        try:
            try:
                ddgs = DDGS(timeout=25)
            except TypeError:
                ddgs = DDGS()
            with ddgs:
                return list(ddgs.images(query, max_results=max_results,
                                        size=size, layout="Wide"))
        except Exception as e:  # network / rate-limit / timeout
            last_exc = e
            time.sleep(1.5)
    if last_exc:
        print(f"    [img] search error ({size}): {type(last_exc).__name__}")
    return []


def search_images(
    query: str,
    min_width: int = 1280,
    min_ar: float = 1.4,
    max_ar: float = 2.2,
    pool: int = 80,
) -> List[dict]:
    """Return landscape, high-res image candidates for one query, best first."""
    raw: List[dict] = []
    for size in ("Wallpaper", "Large"):
        raw += _ddgs_images(query, pool, size)
        if len(raw) >= pool:
            break

    seen = set()
    cands: List[dict] = []
    for r in raw:
        url = r.get("image")
        if not url:
            continue
        w = int(r.get("width") or 0)
        h = int(r.get("height") or 0)
        if w and w < min_width:
            continue
        if not _aspect_ok(w, h, min_ar, max_ar):
            continue
        key = _dedup_key(url)
        if key in seen:
            continue
        seen.add(key)
        cands.append({"url": url, "width": w, "height": h, "score": _score(w, h)})

    cands.sort(key=lambda c: c["score"], reverse=True)
    return cands


def _fetch(url: str, timeout: int = 25) -> Optional[tuple]:
    """Return (bytes, ext) or None."""
    try:
        resp = requests.get(url, headers=_HEADERS, timeout=timeout, stream=True)
        resp.raise_for_status()
        ctype = resp.headers.get("Content-Type", "").split(";")[0].strip().lower()
        if ctype in _VALID_CT:
            ext = _EXT[ctype]
        else:
            lower = url.lower().split("?")[0]
            ext = next((e for e in (".jpg", ".jpeg", ".png", ".webp") if lower.endswith(e)), None)
            if not ext:
                return None
            ext = ".jpg" if ext == ".jpeg" else ext
        data = resp.content
        if len(data) < 15000:
            return None
        return data, ext
    except Exception:
        return None


def collect_images(
    queries: Union[str, List[str]],
    out_dir: str,
    count: int = 4,
    min_width: int = 1280,
    min_ar: float = 1.4,
    max_ar: float = 2.2,
    name_prefix: str = "image",
    dedup: Optional[DedupState] = None,
) -> List[ImageResult]:
    """
    Search across one or more queries and download up to `count` UNIQUE
    landscape, high-resolution images into out_dir. When a shared `dedup`
    state is passed, images already used in other scenes are skipped.
    """
    if isinstance(queries, str):
        queries = [queries]
    if dedup is None:
        dedup = DedupState()

    os.makedirs(out_dir, exist_ok=True)

    # Build a ranked candidate pool from every query (skip URLs already used).
    pooled: List[dict] = []
    local_seen = set()
    for q in queries:
        for c in search_images(q, min_width=min_width, min_ar=min_ar, max_ar=max_ar):
            key = _dedup_key(c["url"])
            if key in local_seen or dedup.url_seen(c["url"]):
                continue
            local_seen.add(key)
            c["query"] = q
            pooled.append(c)

    pooled.sort(key=lambda c: c["score"], reverse=True)

    results: List[ImageResult] = []
    n = 0
    for cand in pooled:
        if n >= count:
            break
        fetched = _fetch(cand["url"])
        if not fetched:
            continue
        data, ext = fetched
        # global content de-dup (exact + perceptual)
        if dedup.is_dup_bytes(data):
            dedup.add_url(cand["url"])
            continue
        path = os.path.join(out_dir, f"{name_prefix}_{n + 1:02d}{ext}")
        try:
            with open(path, "wb") as f:
                f.write(data)
        except OSError:
            continue
        dedup.add_url(cand["url"])
        results.append(ImageResult(
            path=path, source_url=cand["url"], query=cand.get("query", ""),
            width=cand.get("width"), height=cand.get("height"),
        ))
        n += 1
        time.sleep(0.15)

    # Relax once if strict filters starved us (still respecting dedup).
    if n < count and min_width > 800:
        extra = collect_images(
            queries, out_dir, count=count - n,
            min_width=800, min_ar=1.3, max_ar=2.4,
            name_prefix=f"{name_prefix}_alt", dedup=dedup,
        )
        results.extend(extra)

    return results


if __name__ == "__main__":
    import sys
    qs = sys.argv[1:] or ["Scarface 1983 Tony Montana mansion office"]
    state = DedupState()
    res = collect_images(qs, out_dir="/tmp/test_imgs3", count=4, dedup=state)
    print(f"downloaded {len(res)} unique images (PIL={_HAVE_PIL}):")
    for r in res:
        print(f"  {r.path} | {r.width}x{r.height} | {r.source_url[:55]}")
