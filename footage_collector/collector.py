#!/usr/bin/env python3
"""
collector.py  --  Footage Collector
===================================
Give it a video script (transcript) + title. It:
  1. splits the script into ordered scene beats,
  2. for each beat, searches YouTube and downloads a short (~5-6s) cropped clip,
  3. also collects a few relevant images,
  4. saves everything into per-scene folders + a manifest.json.

No API keys needed (YouTube via yt-dlp, images via DuckDuckGo).

NOTE on YouTube downloads:
  YouTube blocks downloads from datacenter / fresh IPs with a
  "Sign in to confirm you're not a bot" error. If you hit that, pass your
  browser cookies, e.g.:
      --cookies-from-browser chrome
  (run this on the machine where you're logged into YouTube in that browser).

Examples
--------
  python collector.py --script scripts/tony_montana.txt \
      --title "WHAT MAKES TONY MONTANA SO TERRIFYING" \
      --out output --images-per-scene 3 --clip-duration 6

  # on your own machine, to get YouTube clips:
  python collector.py --script scripts/tony_montana.txt --out output \
      --cookies-from-browser chrome
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone

import scene_parser
import youtube_clipper as yt
import image_collector as ic


def log(msg: str) -> None:
    print(msg, flush=True)


def derive_title(script_path: str, script_text: str, explicit: str | None) -> str:
    if explicit:
        return explicit
    # try first non-empty line if it looks like a title (short, no period)
    for line in script_text.splitlines():
        line = line.strip()
        if line:
            if len(line) < 90 and not line.endswith((".", "!", "?")):
                return line
            break
    # fall back to filename
    base = os.path.splitext(os.path.basename(script_path))[0]
    return base.replace("_", " ").replace("-", " ").title()


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Collect YouTube clips + images for each scene of a script.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("--script", required=True, help="Path to the script/transcript .txt file")
    p.add_argument("--title", default=None, help="Video title (auto-detected if omitted)")
    p.add_argument("--out", default="output", help="Output directory")
    p.add_argument("--context", default=None,
                   help="Override the global search anchor (e.g. 'Scarface 1983')")

    p.add_argument("--sentences-per-scene", type=int, default=2,
                   help="How many sentences make up one scene/beat")
    p.add_argument("--clip-duration", type=float, default=6.0,
                   help="Length of each cropped clip in seconds")
    p.add_argument("--clips-per-scene", type=int, default=1,
                   help="Clips to download per scene (0 to skip clips)")
    p.add_argument("--images-per-scene", type=int, default=3,
                   help="Images to download per scene (0 to skip images)")

    p.add_argument("--search-n", type=int, default=5,
                   help="YouTube candidate videos to try per scene")
    p.add_argument("--max-height", type=int, default=480,
                   help="Max video resolution to download")
    p.add_argument("--min-image-width", type=int, default=600,
                   help="Minimum image width to accept")

    p.add_argument("--max-scenes", type=int, default=0,
                   help="Limit number of scenes processed (0 = all)")
    p.add_argument("--start-scene", type=int, default=1,
                   help="1-based scene index to start from (for resuming)")

    p.add_argument("--cookies", default=None, help="Path to a cookies.txt file for YouTube")
    p.add_argument("--cookies-from-browser", default=None,
                   help="Browser to read YouTube cookies from (chrome/firefox/edge/...)")
    p.add_argument("--player-client", default=None,
                   help="yt-dlp youtube player_client (android/ios/web/...)")

    p.add_argument("--dry-run", action="store_true",
                   help="Only parse scenes & print queries; download nothing")
    return p


def main(argv=None) -> int:
    args = build_arg_parser().parse_args(argv)

    if not os.path.isfile(args.script):
        log(f"ERROR: script file not found: {args.script}")
        return 2

    with open(args.script, "r", encoding="utf-8") as f:
        script_text = f.read()

    title = derive_title(args.script, script_text, args.title)
    scenes = scene_parser.parse_script(
        title, script_text,
        sentences_per_scene=args.sentences_per_scene,
        context=args.context,
    )

    # apply scene range
    if args.start_scene > 1:
        scenes = [s for s in scenes if s.index >= args.start_scene]
    if args.max_scenes > 0:
        scenes = scenes[:args.max_scenes]

    context = args.context or scene_parser.derive_context(title, script_text, max_terms=2)

    log("=" * 64)
    log(f"  Title    : {title}")
    log(f"  Context  : {context}")
    log(f"  Scenes   : {len(scenes)}  (sentences/scene={args.sentences_per_scene})")
    log(f"  Per scene: {args.clips_per_scene} clip(s) @ {args.clip_duration}s, "
        f"{args.images_per_scene} image(s)")
    log(f"  Output   : {os.path.abspath(args.out)}")
    log("=" * 64)

    if args.dry_run:
        for s in scenes:
            log(f"[{s.index:03d}] q='{s.query}'  kw={s.keywords}")
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
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "settings": {
            "sentences_per_scene": args.sentences_per_scene,
            "clip_duration": args.clip_duration,
            "clips_per_scene": args.clips_per_scene,
            "images_per_scene": args.images_per_scene,
        },
        "scenes": [],
    }
    manifest_path = os.path.join(args.out, "manifest.json")

    def save_manifest():
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)

    totals = {"clips": 0, "images": 0, "clip_fail": 0}
    t0 = time.time()

    for n, scene in enumerate(scenes, 1):
        scene_dir = os.path.join(args.out, scene.slug())
        os.makedirs(scene_dir, exist_ok=True)
        log(f"\n--- Scene {scene.index}/{scenes[-1].index}  ({n}/{len(scenes)}) ---")
        log(f"    text : {scene.text[:90]}{'...' if len(scene.text) > 90 else ''}")
        log(f"    query: {scene.query}")

        # write scene text + query for reference
        with open(os.path.join(scene_dir, "scene.txt"), "w", encoding="utf-8") as f:
            f.write(f"# Scene {scene.index}\n\nQUERY: {scene.query}\n"
                    f"KEYWORDS: {', '.join(scene.keywords)}\n\nTEXT:\n{scene.text}\n")

        entry = {
            "index": scene.index,
            "slug": scene.slug(),
            "text": scene.text,
            "query": scene.query,
            "keywords": scene.keywords,
            "clips": [],
            "images": [],
        }

        # --- clips ---
        for ci in range(args.clips_per_scene):
            out_path = os.path.join(scene_dir, f"clip_{ci + 1:02d}.mp4")
            try:
                res = yt.collect_clip(
                    scene.query, scene.keywords, out_path,
                    duration=args.clip_duration,
                    search_n=args.search_n,
                    max_height=args.max_height,
                    auth=auth,
                )
            except Exception as e:
                log(f"    [clip] error: {type(e).__name__}: {e}")
                res = None
            if res:
                entry["clips"].append(res.to_dict())
                totals["clips"] += 1
                log(f"    [clip] OK  {os.path.basename(res.path)}  "
                    f"<- {res.title[:50]} @ {res.start}s (score {res.match_score})")
            else:
                totals["clip_fail"] += 1
                log(f"    [clip] no clip found/downloaded")

        # --- images ---
        if args.images_per_scene > 0:
            try:
                imgs = ic.collect_images(
                    scene.query, scene_dir,
                    count=args.images_per_scene,
                    min_width=args.min_image_width,
                )
            except Exception as e:
                log(f"    [img] error: {type(e).__name__}: {e}")
                imgs = []
            for im in imgs:
                entry["images"].append(im.to_dict())
            totals["images"] += len(imgs)
            log(f"    [img] downloaded {len(imgs)} image(s)")

        manifest["scenes"].append(entry)
        save_manifest()

    dt = time.time() - t0
    log("\n" + "=" * 64)
    log(f"  DONE in {dt:.0f}s")
    log(f"  clips: {totals['clips']} ok, {totals['clip_fail']} failed | "
        f"images: {totals['images']}")
    log(f"  manifest: {manifest_path}")
    log("=" * 64)
    return 0


if __name__ == "__main__":
    sys.exit(main())
