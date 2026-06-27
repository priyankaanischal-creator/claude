"""
image_collector.py
------------------
Keyless image sourcing using DuckDuckGo image search (ddgs library).
Downloads N relevant images per scene into the scene folder.
"""

from __future__ import annotations

import os
import time
from dataclasses import dataclass, asdict
from typing import List, Optional

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


@dataclass
class ImageResult:
    path: str
    source_url: str
    width: Optional[int] = None
    height: Optional[int] = None

    def to_dict(self) -> dict:
        return asdict(self)


def search_images(query: str, max_results: int = 10, min_width: int = 600) -> List[dict]:
    """Return image candidates from DuckDuckGo (no API key)."""
    out: List[dict] = []
    try:
        with DDGS() as ddgs:
            for r in ddgs.images(query, max_results=max_results * 2):
                w = r.get("width") or 0
                h = r.get("height") or 0
                if min_width and w and w < min_width:
                    continue
                out.append({
                    "url": r.get("image"),
                    "width": w or None,
                    "height": h or None,
                })
                if len(out) >= max_results:
                    break
    except Exception as e:  # network / rate-limit / parsing
        print(f"    [img] search error: {type(e).__name__}: {e}")
    return out


def _download_one(url: str, dest_no_ext: str, timeout: int = 20) -> Optional[str]:
    try:
        resp = requests.get(url, headers=_HEADERS, timeout=timeout, stream=True)
        resp.raise_for_status()
        ctype = resp.headers.get("Content-Type", "").split(";")[0].strip().lower()
        if ctype not in _VALID_CT:
            # guess from URL extension as a fallback
            lower = url.lower()
            ext = next((e for e in (".jpg", ".jpeg", ".png", ".webp") if lower.endswith(e)), None)
            if not ext:
                return None
            ext = ".jpg" if ext == ".jpeg" else ext
        else:
            ext = _EXT[ctype]
        data = resp.content
        if len(data) < 3000:  # skip tiny / broken images
            return None
        path = dest_no_ext + ext
        with open(path, "wb") as f:
            f.write(data)
        return path
    except Exception:
        return None


def collect_images(
    query: str,
    out_dir: str,
    count: int = 3,
    min_width: int = 600,
    name_prefix: str = "image",
) -> List[ImageResult]:
    """Search and download up to `count` images into out_dir."""
    os.makedirs(out_dir, exist_ok=True)
    candidates = search_images(query, max_results=count + 8, min_width=min_width)

    results: List[ImageResult] = []
    n = 0
    for cand in candidates:
        if n >= count:
            break
        url = cand.get("url")
        if not url:
            continue
        dest = os.path.join(out_dir, f"{name_prefix}_{n + 1:02d}")
        path = _download_one(url, dest)
        if path:
            results.append(ImageResult(
                path=path, source_url=url,
                width=cand.get("width"), height=cand.get("height"),
            ))
            n += 1
            time.sleep(0.2)  # be polite
    return results


if __name__ == "__main__":
    import sys
    q = sys.argv[1] if len(sys.argv) > 1 else "Tony Montana Scarface white suit"
    res = collect_images(q, out_dir="/tmp/test_imgs", count=3)
    print(f"downloaded {len(res)} images:")
    for r in res:
        print("  ", r.path, "|", r.width, "x", r.height, "|", r.source_url[:60])
