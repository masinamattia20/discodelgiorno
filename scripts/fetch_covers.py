#!/usr/bin/env python3
"""Scarica le copertine dalla iTunes Search API (gratis, senza chiave).

Legge data/albums.json, interroga iTunes per ogni album, salva la copertina in
assets/covers/<id>.jpg e scrive data/covers.json + data/covers.js con la mappa
id album -> percorso copertina. Idempotente: gli album la cui copertina esiste
gia' vengono saltati, quindi rilanciarlo riempie solo i buchi.

Avvio: python3 scripts/fetch_covers.py
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
ART_SIZE = "500x500bb.jpg" # ingrandisce la miniatura 100x100 di iTunes
DELAY = 0.6 # pausa cortese tra una richiesta e l'altra


def get_json(url):
    """GET con retry/backoff su throttling (429) ed errori transitori."""
    for attempt in range(4):
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code in (403, 429, 500, 502, 503) and attempt < 3:
                time.sleep(2 ** attempt) # 1, 2, 4s
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
    """Toglie le parentesi e la punteggiatura che confondono la ricerca iTunes."""
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
    """Richiede che l'ARTISTA combaci; preferisce i risultati in cui combacia
    anche il titolo dell'album. Mai ripiegare su un risultato non correlato
    (dava copertine sbagliate per titoli generici tipo 'Lungs')."""
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
            return r # artista + album: match forte
        if artist_only is None:
            artist_only = r # artista giusto, titolo variante
    return artist_only


def find_artwork(artist, album):
    """Restituisce l'URL della copertina ad alta risoluzione, o None."""
    terms = []
    for t in (artist + " " + album, clean(artist) + " " + clean(album),
              clean(album) + " " + clean(artist)):
        t = t.strip()
        if t and t not in terms:
            terms.append(t)
    # prima gli album; se lo store album non ha nulla, i brani portano la stessa
    # copertina della raccolta (es. Pavement - Slanted & Enchanted).
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
            print(f"[{i}/{len(albums)}] MISS  {a['artist']} - {a['album']}")
            continue
        try:
            size = download(art, dest)
            covers[a["id"]] = rel
            hits += 1
            print(f"[{i}/{len(albums)}] ok    {a['artist']} - {a['album']} ({size // 1024}KB)")
        except Exception as e:
            misses += 1
            print(f"[{i}/{len(albums)}] FAIL  {a['artist']} - {a['album']}: {e}")
        time.sleep(DELAY)

    payload = json.dumps(covers, ensure_ascii=False, indent=1)
    MAP_JSON.write_text(payload, encoding="utf-8")
    MAP_JS.write_text(
        "// Generato da scripts/fetch_covers.py - non modificare a mano.\n"
        f"window.COVERS = {payload};\n",
        encoding="utf-8",
    )
    print(f"\ncovers: {len(covers)}/{len(albums)} "
          f"(new {hits}, cached {skipped}, missing {misses})")


if __name__ == "__main__":
    sys.exit(main())
