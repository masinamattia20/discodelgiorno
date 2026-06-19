#!/usr/bin/env python3
"""Converte disco_del_giorno.txt in albums.json strutturato.

La lista sorgente mescola due formati:
    "Titolo (anno) - Artista"
    "Artista - Titolo (anno)"

Indizio chiave: il segmento che contiene "(anno)" e' il TITOLO; l'altro
segmento e' l'ARTISTA. Senza anno si ripiega su "Artista - Titolo".
Avvio: python3 scripts/parse.py
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "disco_del_giorno.txt"
OUT = ROOT / "data" / "albums.json"

YEAR_RE = re.compile(r"\((\d{4})\)")

# Alcune righe sono troppo irregolari per le regole generiche: fissate a mano.
OVERRIDES = {
    "Peter Gabriel III - Melt (1980) - Peter Gabriel": ("Peter Gabriel", "Peter Gabriel III (Melt)", 1980),
    "San Francisco's Still Doomed - 1976/78 (1990) - Crime": ("Crime", "San Francisco's Still Doomed (1976/78)", 1990),
    "DNA on DNA (1977-1981) (2004) - DNA": ("DNA", "DNA on DNA (1977-1981)", 2004),
    "II - The Final Option (1993) - Die Krupps": ("Die Krupps", "II - The Final Option", 1993),
    "Disco del giorno Sign O' the Times (1987) - Prince": ("Prince", "Sign O' the Times", 1987),
    "Disco del giorno: 77 (1977) - Talking Heads": ("Talking Heads", "77", 1977),
    "T. Rex - Electric Warrior": ("T. Rex", "Electric Warrior", None),
}


def extract_year(text):
    """Restituisce l'anno di uscita: l'ultimo gruppo (anno) a 4 cifre."""
    years = YEAR_RE.findall(text)
    return int(years[-1]) if years else None


def strip_year(text):
    """Rimuove le parentesi con l'anno e comprime gli spazi."""
    return re.sub(r"\s*\(\d{4}\)\s*", " ", text).strip()


def parse_line(raw):
    line = raw.strip()
    if not line:
        return None
    if line in OVERRIDES:
        artist, album, year = OVERRIDES[line]
        return {"artist": artist, "album": album, "year": year}

    line = re.sub(r"^Disco del giorno:?\s*", "", line)
    # Normalizza i separatori "-" a cui manca lo spazio da un lato:
    # "(1993) -Earth" (senza spazio dopo) e "(1989)- Numb" (senza spazio prima).
    # Un vero separatore ha uno spazio almeno da un lato; i nomi col trattino
    # (es. Sleater-Kinney) non ne hanno, quindi restano intatti.
    line = re.sub(r"\s+-\s*", " - ", line)
    line = re.sub(r"(?<=\S)-\s+", " - ", line)

    year = extract_year(line)
    segments = [s.strip() for s in line.split(" - ")]

    if len(segments) == 1:
        # nessun separatore: tutto il testo e' il titolo, artista sconosciuto
        return {"artist": "", "album": strip_year(segments[0]), "year": year}

    if year is None:
        # nessun anno -> si assume "Artista - Titolo"
        artist = segments[0]
        album = " - ".join(segments[1:])
        return {"artist": artist, "album": album, "year": None}

    # anno presente: il segmento che lo contiene e' il titolo
    year_idx = next((i for i, s in enumerate(segments) if YEAR_RE.search(s)), 0)
    if year_idx == 0:
        album = strip_year(" - ".join(segments[:-1])) if len(segments) > 2 else strip_year(segments[0])
        artist = segments[-1]
    else:
        artist = segments[0]
        album = strip_year(" - ".join(segments[1:]))
    return {"artist": artist.strip(), "album": album.strip(), "year": year}


def slugify(*parts):
    s = " ".join(str(p) for p in parts if p)
    s = s.lower().translate(str.maketrans("àáäâãèéëêìíïîòóöôõùúüûñç", "aaaaaeeeeiiiiooooouuuunc"))
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s or "disco"


def main():
    albums = []
    for raw in SRC.read_text(encoding="utf-8").splitlines():
        rec = parse_line(raw)
        if rec and rec["album"]:
            albums.append(rec)

    albums.sort(key=lambda r: (r["artist"].lower(), r["year"] or 0))

    # id stabile per album (serve a riagganciare le copertine tra un run e l'altro)
    seen = {}
    for rec in albums:
        base = slugify(rec["artist"], rec["album"], rec["year"])
        n = seen.get(base, 0)
        seen[base] = n + 1
        rec["id"] = base if n == 0 else base + "-" + str(n + 1)
    payload = json.dumps(albums, ensure_ascii=False, indent=1)
    OUT.write_text(payload, encoding="utf-8")
    # Scrive anche un wrapper JS puro, cosi' il sito si apre direttamente da
    # file:// senza incappare nel CORS su fetch().
    (OUT.parent / "albums.js").write_text(
        "// Generato da scripts/parse.py - non modificare a mano.\n"
        f"window.ALBUMS = {payload};\n",
        encoding="utf-8",
    )

    no_year = [a for a in albums if a["year"] is None]
    no_artist = [a for a in albums if not a["artist"]]
    print(f"parsed {len(albums)} albums -> {OUT.relative_to(ROOT)}")
    print(f"no year: {len(no_year)} | no artist: {len(no_artist)}")
    for a in no_year:
        print("  NO YEAR:", a)
    for a in no_artist:
        print("  NO ARTIST:", a)


if __name__ == "__main__":
    sys.exit(main())
