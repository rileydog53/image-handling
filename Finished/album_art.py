#!/usr/bin/env python3
"""
Album Artwork Downloader
Uses artwork.dodoapps.io (bendodson.com backend) as primary API.

Rate limit strategy:
  - On rate limit: wait 5s, retry
  - After 30s still rate limited: mark as NEEDS_BROWSER, move on
  - Claude handles NEEDS_BROWSER albums via Chrome / bendodson.com

Usage:
  Single:  python3 album_art.py "album artist"
  Batch:   python3 album_art.py --batch list.md
           (parses markdown tables or plain "Album - Artist" lines)
"""

import requests
import re
import sys
import time
import json
from pathlib import Path

ARTWORK_DIR = Path.home() / "Desktop" / "Claude" / "Storage" / "Album Artwork"
PRIMARY_API  = "https://artwork.dodoapps.io/"
RETRY_WAIT   = 5    # seconds between rate-limit retries
BROWSER_AFTER = 30  # seconds before giving up and flagging for browser fallback

NEEDS_BROWSER = "NEEDS_BROWSER"
NO_RESULTS    = "NO_RESULTS"


def safe_name(s):
    return re.sub(r'[<>:"/\\|?*]', "", s).strip()


# ── Primary API (artwork.dodoapps.io) ─────────────────────────────────────────

def api_search(query):
    """
    Returns dict with keys: artist, name, large (uncompressed URL), thumb
    Returns None on no results.
    Raises RateLimitError if rate limited.
    """
    r = requests.post(
        PRIMARY_API,
        json={"search": query, "storefront": "us", "type": "album"},
        timeout=15,
    )
    if r.status_code == 429 or not r.text.strip():
        raise RateLimitError()
    images = r.json().get("images", [])
    return images[0] if images else None


class RateLimitError(Exception):
    pass


# ── Download a URL to disk ─────────────────────────────────────────────────────

def save_image(url, artist, album, output_dir):
    r = requests.get(url, timeout=20)
    if r.status_code != 200:
        return None
    ct  = r.headers.get("content-type", "")
    ext = ".png" if "png" in ct else ".jpg"
    fp  = output_dir / f"{safe_name(artist)} - {safe_name(album)}{ext}"
    fp.write_bytes(r.content)
    return fp, len(r.content) // 1024


# ── Core download with rate-limit retry ───────────────────────────────────────

def download(query, output_dir=None):
    """
    Returns:
      Path        – success
      NO_RESULTS  – album not found on Apple Music
      NEEDS_BROWSER – still rate limited after BROWSER_AFTER seconds
    """
    if output_dir is None:
        output_dir = ARTWORK_DIR
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    deadline = time.time() + BROWSER_AFTER
    attempt  = 0

    while True:
        try:
            img = api_search(query)
            break                          # success or no-results — exit retry loop
        except RateLimitError:
            elapsed = BROWSER_AFTER - (deadline - time.time())
            if time.time() >= deadline:
                print(f"  ⚠  rate limited for {BROWSER_AFTER}s → flagging for browser")
                return NEEDS_BROWSER
            attempt += 1
            print(f"  rate limited (attempt {attempt}, {elapsed:.0f}s elapsed) — waiting {RETRY_WAIT}s…")
            time.sleep(RETRY_WAIT)
        except Exception as e:
            print(f"  API error: {e}")
            return NO_RESULTS

    if img is None:
        print("  no results on Apple Music")
        return NO_RESULTS

    artist = img.get("artist", "Unknown")
    album  = img.get("name",   "Unknown")
    url    = img.get("large") or img.get("thumb")
    print(f"  matched: {artist} — {album}")

    try:
        fp, kb = save_image(url, artist, album, output_dir)
        print(f"  saved ({kb} KB): {fp.name}")
        return fp
    except Exception as e:
        print(f"  download failed: {e}")
        return NO_RESULTS


# ── List parser ───────────────────────────────────────────────────────────────

def parse_list(path):
    """
    Accepts:
      • CSV with headers Number,Artist,Album (multi-artist separated by ;)
      • Markdown table:  | Album | Artist |
      • Plain lines:     Album - Artist
                         Album by Artist
    Returns list of (album, artist) tuples.
    """
    import csv as _csv
    text = Path(path).read_text()

    # CSV detection: first non-empty line has comma-separated headers
    first = next((l for l in text.splitlines() if l.strip()), "")
    if re.match(r"(?i)number\s*,\s*artist\s*,\s*album", first):
        pairs = []
        reader = _csv.DictReader(text.splitlines())
        for row in reader:
            album  = row.get("Album", "").strip()
            artist = row.get("Artist", "").strip()
            if album and artist:
                # use first artist when multiple are joined by ;
                artist = artist.split(";")[0].strip()
                pairs.append((album, artist))
        return pairs

    pairs = []
    for line in text.splitlines():
        # Markdown table row
        m = re.match(r"\|\s*(.+?)\s*\|\s*(.+?)\s*\|", line)
        if m and m.group(1) not in ("Album", "---", "-"):
            pairs.append((m.group(1), m.group(2)))
            continue
        # "Album - Artist" or "Album by Artist"
        m = re.match(r"^(.+?)\s+(?:-|by)\s+(.+)$", line.strip())
        if m:
            pairs.append((m.group(1).strip(), m.group(2).strip()))
    return pairs


# ── Batch runner ──────────────────────────────────────────────────────────────

def run_batch(pairs, output_dir=None):
    total        = len(pairs)
    ok           = []
    no_results   = []
    needs_browser = []

    for i, (album, artist) in enumerate(pairs, 1):
        # Skip already downloaded
        existing = list((output_dir or ARTWORK_DIR).glob(f"*{safe_name(album[:20])}*"))
        if existing:
            print(f"[{i:3}/{total}] SKIP (exists): {artist} — {album}")
            ok.append((album, artist))
            continue

        print(f"[{i:3}/{total}] {artist} — {album}")
        query  = f"{album} {artist}"
        result = download(query, output_dir)

        if isinstance(result, Path):
            ok.append((album, artist))
        elif result == NEEDS_BROWSER:
            needs_browser.append((album, artist))
        else:
            no_results.append((album, artist))

    return ok, no_results, needs_browser


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    if sys.argv[1] == "--batch":
        if len(sys.argv) < 3:
            print("Usage: python3 album_art.py --batch list.md")
            sys.exit(1)
        pairs = parse_list(sys.argv[2])
        # Optional slice flags
        start = 0
        limit = None
        if "--start" in sys.argv:
            start = int(sys.argv[sys.argv.index("--start") + 1])
        if "--limit" in sys.argv:
            limit = int(sys.argv[sys.argv.index("--limit") + 1])
        pairs = pairs[start : (start + limit) if limit else None]
        print(f"Processing rows {start}–{start + len(pairs) - 1} ({len(pairs)} albums)\n")
        ok, no_results, needs_browser = run_batch(pairs)
        print(f"\n{'='*50}")
        print(f"Done: {len(ok)} saved, {len(no_results)} not on Apple Music, {len(needs_browser)} need browser")
        if needs_browser:
            print(f"\nFlagged for browser fallback:")
            for album, artist in needs_browser:
                print(f"  {artist} — {album}")
            # Write to file for Claude to pick up
            out = Path("~/Desktop/Claude/needs_browser.json").expanduser()
            out.write_text(json.dumps(needs_browser, indent=2))
            print(f"\n→ Saved to {out} for Claude browser pass")
        if no_results:
            print(f"\nNot found on Apple Music:")
            for album, artist in no_results:
                print(f"  {artist} — {album}")
    else:
        query = " ".join(sys.argv[1:])
        print(f"Searching: {query}")
        download(query)
