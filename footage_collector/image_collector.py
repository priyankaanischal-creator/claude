"""
image_collector.py
------------------
Keyless image sourcing using DuckDuckGo image search (ddgs library).

Quality focused for 16:9 video:
  - asks DuckDuckGo for Large / Wallpaper, Wide-layout images
  - filters to LANDSCAPE, high-resolution images (min width, sane aspect ratio)
  - ranks candidates by resolution + closeness to 16:9 (1.78)
  - accepts MULTIPLE queries per scene and de-duplicates results

Downloads the top N images per scene into the scene folder.
"""

from __future__ import annotations

import os
import time
from dataclasses import dataclass, asdict
from typing import List, Optional, Union
from urllib.parse import urlparse

import requests

try:
    from ddgs import DDGS
except ImportError:  # older package name
    from duckduckgo_search import DDGS  # type: ignore


_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}

_VALID_CT = ("image/jpeg", "image/jpg", "image/png", "image/webp")
_EXT = {"image/jpeg": ".jpg", "image/jpg": ".jpg", "image/png": ".png", "image/webp": ".webp"}

TARGET_AR = 16 / 9  # 1.778


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
    """Higher is better: reward resolution, penalise distance from 16:9."""
    if not w or not h:
        return 0.0
    ar = w / h
    ar_penalty = abs(ar - TARGET_AR) * 1000  # strongly prefer ~16:9
    res_bonus = min(w, 3840)                 # cap so 8K doesn't dominate
    return res_bonus - ar_penalty


def _dedup_key(url: str) -> str:
    p = urlparse(url)
    return (p.netloc + p.path).lower()


def search_images(
    query: str,
    want: int = 5,
    min_width: int = 1280,
    min_ar: float = 1.4,
    max_ar: float = 2.2,
    pool: int = 60,
) -> List[dict]:
    """
    Return landscape, high-res image candidates for one query, best first.
    """
    raw: List[dict] = []
    # Try a couple of size buckets to maximise high-res hits.
    for size in ("Wallpaper", "Large"):
        try:
            with DDGS() as ddgs:
                for r in ddgs.images(query, max_results=pool, size=size, layout="Wide"):
                    raw.append(r)
        except Exception as e:
            print(f"    [img] search error ({size}): {type(e).__name__}: {e}")
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


def _download_one(url: str, dest_no_ext: str, min_width: int, timeout: int = 25) -> Optional[str]:
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
        if len(data) < 15000:  # skip tiny / thumbnail-ish files
            return None
        path = dest_no_ext + ext
        with open(path, "wb") as f:
            f.write(data)
        return path
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
) -> List[ImageResult]:
    """
    Search across one or more queries and download up to `count` landscape,
    high-resolution images into out_dir. Results de-duplicated across queries.
    """
    if isinstance(queries, str):
        queries = [queries]

    os.makedirs(out_dir, exist_ok=True)

    # Gather a ranked candidate pool from every query.
    pooled: List[dict] = []
    seen_urls = set()
    for q in queries:
        for c in search_images(q, want=count, min_width=min_width,
                               min_ar=min_ar, max_ar=max_ar):
            key = _dedup_key(c["url"])
            if key in seen_urls:
                continue
            seen_urls.add(key)
            c["query"] = q
            pooled.append(c)

    pooled.sort(key=lambda c: c["score"], reverse=True)

    results: List[ImageResult] = []
    n = 0
    for cand in pooled:
        if n >= count:
            break
        dest = os.path.join(out_dir, f"{name_prefix}_{n + 1:02d}")
        path = _download_one(cand["url"], dest, min_width)
        if path:
            results.append(ImageResult(
                path=path, source_url=cand["url"], query=cand.get("query", ""),
                width=cand.get("width"), height=cand.get("height"),
            ))
            n += 1
            time.sleep(0.15)

    # Fallback: if strict filters starved us, relax once (lower res floor).
    if n < count and min_width > 800:
        extra = collect_images(
            queries, out_dir, count=count - n,
            min_width=800, min_ar=1.3, max_ar=2.4,
            name_prefix=f"{name_prefix}_alt",
        )
        results.extend(extra)

    return results


if __name__ == "__main__":
    import sys
    q = sys.argv[1:] or ["Scarface 1983 Tony Montana mansion office white suit"]
    res = collect_images(q, out_dir="/tmp/test_imgs2", count=4)
    print(f"downloaded {len(res)} images:")
    for r in res:
        print(f"  {r.path} | {r.width}x{r.height} | q='{r.query}' | {r.source_url[:55]}")
