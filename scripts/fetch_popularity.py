#!/usr/bin/env python3
"""Scarica la popolarita' degli album dalla Last.fm API (gratis, solo API key).

Legge data/albums.json, interroga album.getInfo per ogni album, legge il numero
di ascoltatori unici ("listeners") e scrive la mappa id album -> listeners in
data/popularity.json + data/popularity.js. File separato (come le copertine),
cosi' sopravvive alle rigenerazioni di scripts/parse.py.

Serve una API key Last.fm (https://www.last.fm/api/account/create), esportata
come variabile d'ambiente (nessun secret: le read pubbliche non lo richiedono):

    export LASTFM_API_KEY="xxx"

Idempotente: gli album che hanno gia' un valore vengono saltati, quindi
rilanciarlo riempie solo i buchi. Per riscaricare tutto: --force.

Avvio: python3 scripts/fetch_popularity.py
"""
import json
import os
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
MAP_JSON = ROOT / "data" / "popularity.json"
MAP_JS = ROOT / "data" / "popularity.js"

API = "http://ws.audioscrobbler.com/2.0/?"
UA = "disco-del-giorno/1.0 (open-source fan project)"
DELAY = 0.25  # pausa cortese tra una richiesta e l'altra


def get_json(url):
    """GET con retry/backoff su throttling (429) ed errori transitori."""
    for attempt in range(4):
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503) and attempt < 3:
                time.sleep(2 ** attempt)  # 1, 2, 4s
                continue
            raise
        except Exception:
            if attempt < 3:
                time.sleep(2 ** attempt)
                continue
            raise


STOP = {"the", "and", "a", "of"}


def fold(s):
    s = unicodedata.normalize("NFD", s or "").encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def tokens(s):
    """Insieme di parole significative (scarta the/and/a/of e '&')."""
    return {w for w in fold(s).split() if w and w not in STOP}


def artist_matches(want, got):
    """Vero se gli artisti combaciano a livello di token (tollera & vs And,
    prefisso The, ordine). Un insieme sottoinsieme dell'altro basta."""
    wa, gg = tokens(want), tokens(got)
    if not wa or not gg:
        return False
    return wa <= gg or gg <= wa


def find_listeners(api_key, artist, album):
    """Restituisce il numero di ascoltatori unici dell'album, o None.

    autocorrect=1 lascia che Last.fm sistemi refusi/varianti. Si verifica che
    l'artista restituito combaci, per non contare un album omonimo sbagliato.
    """
    url = API + urllib.parse.urlencode({
        "method": "album.getinfo",
        "api_key": api_key,
        "artist": artist,
        "album": album,
        "autocorrect": 1,
        "format": "json",
    })
    try:
        data = get_json(url)
    except Exception as e:
        print("  ! query failed:", e)
        return None
    info = data.get("album")
    if not info:
        return None
    if not artist_matches(artist, info.get("artist", "")):
        return None  # artista non combacia: match sbagliato
    listeners = info.get("listeners")
    return int(listeners) if listeners not in (None, "") else None


def main():
    api_key = os.environ.get("LASTFM_API_KEY")
    if not api_key:
        sys.exit("ERRORE: esporta LASTFM_API_KEY (vedi docstring dello script).")

    force = "--force" in sys.argv[1:]
    albums = json.loads(ALBUMS.read_text(encoding="utf-8"))
    pop = {}
    if MAP_JSON.exists() and not force:
        pop = json.loads(MAP_JSON.read_text(encoding="utf-8"))

    hits = misses = skipped = 0
    for i, a in enumerate(albums, 1):
        if not force and a["id"] in pop:
            skipped += 1
            continue
        value = find_listeners(api_key, a["artist"], a["album"])
        time.sleep(DELAY)
        if value is None:
            misses += 1
            print(f"[{i}/{len(albums)}] MISS  {a['artist']} - {a['album']}")
            continue
        pop[a["id"]] = value
        hits += 1
        print(f"[{i}/{len(albums)}] ok    {a['artist']} - {a['album']} ({value} listeners)")

    payload = json.dumps(pop, ensure_ascii=False, indent=1)
    MAP_JSON.write_text(payload, encoding="utf-8")
    MAP_JS.write_text(
        "// Generato da scripts/fetch_popularity.py - non modificare a mano.\n"
        f"window.POPULARITY = {payload};\n",
        encoding="utf-8",
    )
    print(f"\npopularity: {len(pop)}/{len(albums)} "
          f"(new {hits}, cached {skipped}, missing {misses})")


if __name__ == "__main__":
    sys.exit(main())
