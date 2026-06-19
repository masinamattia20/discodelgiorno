#!/usr/bin/env python3
"""Download album cover art from the iTunes Search API (free, no key).

Reads data/albums.json, queries iTunes for each album, saves the artwork to
assets/covers/<id>.jpg and writes data/covers.json + data/covers.js mapping
album id -> cover path. Idempotent: albums whose cover already exists are
skipped, so re-running only fills the gaps.

Run: python3 scripts/fetch_covers.py
"""
import json
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ALBUMS = ROOT / "data" / "albums.json"
COVERS_DIR = ROOT / "assets" / "covers"
MAP_JSON = ROOT / "data" / "covers.json"
MAP_JS = ROOT / "data" / "covers.js"

SEARCH = "https://itunes.apple.com/search?"
UA = "disco-del-giorno/1.0 (open-source fan project)"
ART_SIZE = "500x500bb.jpg"        # upscale the 100x100 thumbnail iTunes returns
DELAY = 0.6                        # polite gap between requests


def get_json(url):
    """GET with retry/backoff on throttling (429) and transient errors."""
    for attempt in range(4):
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code in (403, 429, 500, 502, 503) and attempt < 3:
                time.sleep(2 ** attempt)  # 1, 2, 4s
                continue
            raise
        except Exception:
            if attempt < 3:
                time.sleep(2 ** attempt)
                continue
            raise


def fold(s):
    s = unicodedata.normalize("NFD", s or "").encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def clean(s):
    """Drop parentheticals and punctuation that throw iTunes search off."""
    s = re.sub(r"\([^)]*\)", " ", s or "")
    s = re.sub(r"[^\w\s&]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def search(term, entity):
    url = SEARCH + urllib.parse.urlencode({
        "term": term, "entity": entity, "limit": 8, "country": "US",
    })
    try:
        data = get_json(url)
    except Exception as e:
        print("  ! query failed:", e)
        return []
    return data.get("results", [])


def pick(results, artist, album):
    """Require the ARTIST to match; prefer results whose album title also
    matches. Never fall back to an unrelated result (that gave wrong covers
    for generic titles like 'Lungs')."""
    wa = fold(clean(artist))
    wl = fold(clean(album))
    artist_only = None
    for r in results:
        art = fold(r.get("artistName", ""))
        name = fold(r.get("collectionName", ""))
        artist_match = bool(wa) and (wa in art or art in wa)
        if not artist_match:
            continue
        album_match = bool(wl) and (wl in name or name in wl)
        if album_match:
            return r                      # artist + album: strong match
        if artist_only is None:
            artist_only = r               # artist right, title variant
    return artist_only


def find_artwork(artist, album):
    """Return a high-res artwork URL for the album, or None."""
    terms = []
    for t in (artist + " " + album, clean(artist) + " " + clean(album),
              clean(album) + " " + clean(artist)):
        t = t.strip()
        if t and t not in terms:
            terms.append(t)
    # albums first; if the album store has nothing, songs carry the same
    # collection artwork (e.g. Pavement — Slanted & Enchanted).
    for entity in ("album", "song"):
        for term in terms:
            r = pick(search(term, entity), artist, album)
            time.sleep(DELAY)
            if r and r.get("artworkUrl100"):
                return re.sub(r"100x100bb\.jpg$", ART_SIZE, r["artworkUrl100"])
    return None


def download(url, dest):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = r.read()
    dest.write_bytes(data)
    return len(data)


def main():
    COVERS_DIR.mkdir(parents=True, exist_ok=True)
    albums = json.loads(ALBUMS.read_text(encoding="utf-8"))

    covers = {}
    hits = misses = skipped = 0
    for i, a in enumerate(albums, 1):
        dest = COVERS_DIR / (a["id"] + ".jpg")
        rel = "assets/covers/" + dest.name
        if dest.exists() and dest.stat().st_size > 0:
            covers[a["id"]] = rel
            skipped += 1
            continue

        art = find_artwork(a["artist"], a["album"])
        time.sleep(DELAY)
        if not art:
            misses += 1
            print(f"[{i}/{len(albums)}] MISS  {a['artist']} — {a['album']}")
            continue
        try:
            size = download(art, dest)
            covers[a["id"]] = rel
            hits += 1
            print(f"[{i}/{len(albums)}] ok    {a['artist']} — {a['album']} ({size // 1024}KB)")
        except Exception as e:
            misses += 1
            print(f"[{i}/{len(albums)}] FAIL  {a['artist']} — {a['album']}: {e}")
        time.sleep(DELAY)

    payload = json.dumps(covers, ensure_ascii=False, indent=1)
    MAP_JSON.write_text(payload, encoding="utf-8")
    MAP_JS.write_text(
        "// Generated by scripts/fetch_covers.py — do not edit by hand.\n"
        f"window.COVERS = {payload};\n",
        encoding="utf-8",
    )
    print(f"\ncovers: {len(covers)}/{len(albums)} "
          f"(new {hits}, cached {skipped}, missing {misses})")


if __name__ == "__main__":
    sys.exit(main())
