#!/usr/bin/env python3
"""
collector.py  --  Footage Collector
===================================
Give it a video script (transcript) + title, OR a curated "plan" file. It:
  1. splits the script into paragraph-sized scenes (or reads them from a plan),
  2. for each scene, searches YouTube and downloads short (~5-6s) cropped clips,
  3. collects several high-resolution, 16:9-friendly images,
  4. saves everything into per-scene folders + a manifest.json.

No API keys needed (YouTube via yt-dlp, images via DuckDuckGo).

Two ways to drive it
--------------------
1) Automatic (heuristic) from a raw script:
     python collector.py --script scripts/tony_montana.txt --words-per-scene 150

2) Curated plan (best relevance) — a JSON file that defines each scene plus
   hand-picked image_queries and clip_queries:
     python collector.py --plan plans/scarface_plan.json --out output

NOTE on YouTube downloads
-------------------------
  YouTube blocks downloads from datacenter / fresh IPs with a
  "Sign in to confirm you're not a bot" error. On your own machine, pass your
  browser cookies to fix it:
     --cookies-from-browser chrome
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List

import scene_parser
import youtube_clipper as yt
import image_collector as ic


def log(msg: str) -> None:
    print(msg, flush=True)


@dataclass
class SceneSpec:
    index: int
    text: str
    image_queries: List[str] = field(default_factory=list)
    clip_queries: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    summary: str = ""

    def slug(self) -> str:
        return f"scene_{self.index:03d}"


# --- building scene specs ---------------------------------------------------

def specs_from_script(title, script_text, args) -> tuple:
    scenes = scene_parser.parse_script(
        title, script_text,
        sentences_per_scene=args.sentences_per_scene,
        words_per_scene=args.words_per_scene or None,
        context=args.context,
    )
    context = args.context or scene_parser.derive_context(title, script_text, max_terms=2)
    specs = [
        SceneSpec(
            index=s.index, text=s.text,
            image_queries=[s.query], clip_queries=[s.query],
            keywords=s.keywords,
        )
        for s in scenes
    ]
    return specs, title, context


def specs_from_plan(plan_path, args) -> tuple:
    with open(plan_path, "r", encoding="utf-8") as f:
        plan = json.load(f)
    title = args.title or plan.get("title", "Untitled")
    context = args.context or plan.get("context", "")
    specs: List[SceneSpec] = []
    for i, sc in enumerate(plan.get("scenes", []), 1):
        iq = sc.get("image_queries") or ([sc["query"]] if sc.get("query") else [])
        cq = sc.get("clip_queries") or ([sc["query"]] if sc.get("query") else [])
        # prefix the global context for extra anchoring if not already present
        if context:
            iq = [q if context.lower() in q.lower() else f"{q}" for q in iq]
        specs.append(SceneSpec(
            index=i,
            text=sc.get("text", "") or sc.get("summary", ""),
            summary=sc.get("summary", ""),
            image_queries=iq,
            clip_queries=cq,
            keywords=sc.get("keywords", []),
        ))
    return specs, title, context


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Collect YouTube clips + images for each scene of a script.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    src = p.add_argument_group("input (one of --script or --plan)")
    src.add_argument("--script", default=None, help="Path to a raw script/transcript .txt")
    src.add_argument("--plan", default=None,
                     help="Path to a curated plan JSON (scenes + image/clip queries)")

    p.add_argument("--title", default=None, help="Video title (auto-detected if omitted)")
    p.add_argument("--out", default="output", help="Output directory")
    p.add_argument("--context", default=None,
                   help="Global search anchor (e.g. 'Scarface 1983 Tony Montana')")

    p.add_argument("--words-per-scene", type=int, default=150,
                   help="Paragraph size in words (script mode). 0 = use sentences")
    p.add_argument("--sentences-per-scene", type=int, default=2,
                   help="Sentences per scene when --words-per-scene is 0")

    p.add_argument("--clip-duration", type=float, default=5.0,
                   help="Length of each cropped clip in seconds (3-5s recommended)")
    p.add_argument("--clips-per-scene", type=int, default=2,
                   help="Clips to download per scene (0 to skip clips)")
    p.add_argument("--images-per-scene", type=int, default=4,
                   help="Images to download per scene (0 to skip images)")

    p.add_argument("--search-n", type=int, default=5,
                   help="YouTube candidate videos to try per clip query")
    p.add_argument("--max-height", type=int, default=720,
                   help="Max video resolution to download")
    p.add_argument("--min-image-width", type=int, default=1280,
                   help="Minimum image width (px) — keeps HD/landscape only")

    p.add_argument("--max-scenes", type=int, default=0,
                   help="Limit number of scenes processed (0 = all)")
    p.add_argument("--start-scene", type=int, default=1,
                   help="1-based scene index to start from (for resuming)")

    p.add_argument("--cookies", default=None, help="Path to a cookies.txt for YouTube")
    p.add_argument("--cookies-from-browser", default=None,
                   help="Browser to read YouTube cookies from (chrome/firefox/edge/...)")
    p.add_argument("--player-client", default=None,
                   help="yt-dlp youtube player_client (android/ios/web/...)")

    p.add_argument("--dry-run", action="store_true",
                   help="Only build scenes & print queries; download nothing")
    return p


def main(argv=None) -> int:
    args = build_arg_parser().parse_args(argv)

    if not args.script and not args.plan:
        log("ERROR: provide --script <file> or --plan <file>")
        return 2

    if args.plan:
        if not os.path.isfile(args.plan):
            log(f"ERROR: plan file not found: {args.plan}")
            return 2
        specs, title, context = specs_from_plan(args.plan, args)
        mode = f"plan ({os.path.basename(args.plan)})"
    else:
        if not os.path.isfile(args.script):
            log(f"ERROR: script file not found: {args.script}")
            return 2
        with open(args.script, "r", encoding="utf-8") as f:
            script_text = f.read()
        # title auto-detect from first short line / filename
        title = args.title
        if not title:
            for line in script_text.splitlines():
                line = line.strip()
                if line:
                    title = line if (len(line) < 90 and not line.endswith((".", "!", "?"))) \
                        else os.path.splitext(os.path.basename(args.script))[0].replace("_", " ").title()
                    break
        specs, title, context = specs_from_script(title, script_text, args)
        mode = "script"

    # scene range
    if args.start_scene > 1:
        specs = [s for s in specs if s.index >= args.start_scene]
    if args.max_scenes > 0:
        specs = specs[:args.max_scenes]

    log("=" * 66)
    log(f"  Title    : {title}")
    log(f"  Context  : {context}")
    log(f"  Mode     : {mode}")
    log(f"  Scenes   : {len(specs)}")
    log(f"  Per scene: {args.clips_per_scene} clip(s) @ {args.clip_duration}s, "
        f"{args.images_per_scene} image(s) (min width {args.min_image_width}px)")
    log(f"  Output   : {os.path.abspath(args.out)}")
    log("=" * 66)

    if args.dry_run:
        for s in specs:
            log(f"[{s.index:03d}] {s.summary or s.text[:60]}")
            for q in s.image_queries:
                log(f"      IMG : {q}")
            for q in s.clip_queries:
                log(f"      CLIP: {q}")
        return 0

    auth = yt.YtAuth(
        cookies_file=args.cookies,
        cookies_from_browser=args.cookies_from_browser,
        player_client=args.player_client,
    )

    os.makedirs(args.out, exist_ok=True)
    manifest = {
        "title": title,
        "context": context,
        "mode": mode,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "settings": {
            "clip_duration": args.clip_duration,
            "clips_per_scene": args.clips_per_scene,
            "images_per_scene": args.images_per_scene,
            "min_image_width": args.min_image_width,
        },
        "scenes": [],
    }
    manifest_path = os.path.join(args.out, "manifest.json")

    def save_manifest():
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)

    totals = {"clips": 0, "images": 0, "clip_fail": 0}
    t0 = time.time()
    last_idx = specs[-1].index if specs else 0
    dedup = ic.DedupState()  # shared across ALL scenes -> no repeated images

    for n, scene in enumerate(specs, 1):
        scene_dir = os.path.join(args.out, scene.slug())
        os.makedirs(scene_dir, exist_ok=True)
        log(f"\n--- Scene {scene.index}/{last_idx}  ({n}/{len(specs)}) ---")
        if scene.summary:
            log(f"    about : {scene.summary}")
        log(f"    img q : {scene.image_queries}")
        log(f"    clip q: {scene.clip_queries}")

        with open(os.path.join(scene_dir, "scene.txt"), "w", encoding="utf-8") as f:
            f.write(f"# Scene {scene.index}\n")
            if scene.summary:
                f.write(f"\nSUMMARY: {scene.summary}\n")
            f.write(f"\nIMAGE QUERIES:\n" + "\n".join(f"  - {q}" for q in scene.image_queries))
            f.write(f"\n\nCLIP QUERIES:\n" + "\n".join(f"  - {q}" for q in scene.clip_queries))
            f.write(f"\n\nTEXT:\n{scene.text}\n")

        entry = {
            "index": scene.index, "slug": scene.slug(),
            "summary": scene.summary, "text": scene.text,
            "image_queries": scene.image_queries,
            "clip_queries": scene.clip_queries,
            "clips": [], "images": [],
        }

        # --- clips: try each clip query until enough succeed ---
        got_clips = 0
        used_video_ids = set()  # avoid the same video twice in one scene
        for ci in range(args.clips_per_scene):
            query = scene.clip_queries[ci % len(scene.clip_queries)] if scene.clip_queries else ""
            if not query:
                break
            out_path = os.path.join(scene_dir, f"clip_{ci + 1:02d}.mp4")
            kw = (query.split() + scene.keywords)
            try:
                res = yt.collect_clip(
                    query, kw, out_path,
                    duration=args.clip_duration,
                    search_n=args.search_n,
                    max_height=args.max_height,
                    auth=auth,
                    exclude_ids=used_video_ids,
                )
            except Exception as e:
                log(f"    [clip] error: {type(e).__name__}: {e}")
                res = None
            if res:
                used_video_ids.add(res.video_id)
                entry["clips"].append(res.to_dict())
                totals["clips"] += 1
                got_clips += 1
                log(f"    [clip] OK  {os.path.basename(res.path)} <- "
                    f"{res.title[:46]} @ {res.start}s (match {res.match_score})")
            else:
                totals["clip_fail"] += 1
                log(f"    [clip] none for: {query}")

        # --- images: pooled across all image queries ---
        if args.images_per_scene > 0:
            try:
                imgs = ic.collect_images(
                    scene.image_queries, scene_dir,
                    count=args.images_per_scene,
                    min_width=args.min_image_width,
                    dedup=dedup,
                )
            except Exception as e:
                log(f"    [img] error: {type(e).__name__}: {e}")
                imgs = []
            for im in imgs:
                entry["images"].append(im.to_dict())
            totals["images"] += len(imgs)
            sizes = ", ".join(f"{im.width}x{im.height}" for im in imgs if im.width)
            log(f"    [img] downloaded {len(imgs)} image(s)  [{sizes}]")

        manifest["scenes"].append(entry)
        save_manifest()

    dt = time.time() - t0
    log("\n" + "=" * 66)
    log(f"  DONE in {dt:.0f}s")
    log(f"  clips: {totals['clips']} ok, {totals['clip_fail']} failed | "
        f"images: {totals['images']}")
    log(f"  manifest: {manifest_path}")
    log("=" * 66)
    return 0


if __name__ == "__main__":
    sys.exit(main())
