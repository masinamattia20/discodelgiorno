# Disco del Giorno

Archivio open source, fan-made, dei dischi consigliati da **Federico Frusciante**.
Sito statico: cerca, ordina (artista/titolo/anno) e sfoglia ~500 dischi, 25 alla volta, con copertine, un "disco del giorno" che cambia ogni
giorno, e una vista estesa (clic su un disco) con link a Spotify, YouTube, Amazon, Discogs e RateYourMusic.

Repo: <https://github.com/masinamattia20/discodelgiorno>

> Progetto non ufficiale. Nessuna affiliazione con Federico Frusciante.

## Struttura

```
discodelgiorno/          # radice della repo
├── index.html          # markup
├── assets/
│   ├── styles.css      # font di sistema, zero dipendenze
│   ├── app.js          # ricerca, filtri, modal, disco del giorno (vanilla JS)
│   └── covers/         # copertine .jpg scaricate (una per disco trovato)
├── data/
│   ├── disco_del_giorno.txt   # lista sorgente (una riga per disco)
│   ├── albums.json            # dati generati (canonico, riusabile)
│   ├── albums.js              # stessi dati come window.ALBUMS (per file://)
│   ├── covers.json            # mappa id -> percorso copertina
│   └── covers.js              # stessa mappa come window.COVERS (per file://)
└── scripts/
    ├── parse.py        # converte il .txt in albums.json + albums.js (+ id stabile)
    └── fetch_covers.py # scarica le copertine da iTunes -> assets/covers/ + covers.js
```

## Avvio

Clona la repo:

```bash
git clone https://github.com/masinamattia20/discodelgiorno.git
cd discodelgiorno
```

Apri `index.html` nel browser, oppure servi la cartella:

```bash
python3 -m http.server 8000
# poi apri http://localhost:8000
```

`albums.js` permette l'apertura diretta via `file://` senza problemi di CORS.

## Aggiornare la lista

1. Modifica `data/disco_del_giorno.txt` (un disco per riga).
   Formati accettati: `Titolo (anno) - Artista` oppure `Artista - Titolo (anno)`.
2. Rigenera i dati:

   ```bash
   python3 scripts/parse.py
   ```

Il parser deduce automaticamente quale lato è il titolo (quello con l'anno) e
quale l'artista, gestendo gli errori tramite la tabella `OVERRIDES`.

## Copertine

```bash
python3 scripts/fetch_covers.py
```

Scarica le copertine dalla [iTunes Search API](https://performance-partners.apple.com/search-api)
(gratis, senza chiave) in `assets/covers/` e scrive la mappa `covers.json` +
`covers.js`. È **idempotente**: rilanciandolo scarica solo le copertine mancanti,
con retry/backoff in caso di throttling. I dischi senza copertina mostrano un
placeholder con le iniziali. Le copertine sono opere protette: incluse a scopo
illustrativo per un progetto non commerciale.

## Tecnologia

HTML + CSS + JavaScript vanilla, font di sistema. Nessun framework, nessun font
esterno, nessun tracker, nessuna build, nessuna chiamata API a runtime (le
copertine sono pre-scaricate).

## Contribuire (Pull Request)

Le PR si aprono sulla repo:
<https://github.com/masinamattia20/discodelgiorno>

Ogni contributo è benvenuto. Regole:

- **Approvazione obbligatoria.** Qualsiasi modifica dev'essere approvata da
  [@masinamattia20](https://github.com/masinamattia20) prima del merge. Nessuna PR
  viene unita senza la sua revisione esplicita, anche se i controlli automatici
  sono verdi.
- **L'aggiunta di un disco richiede una prova.** Per aggiungere un disco devi
  fornire la **prova** che Frusciante l'abbia effettivamente consigliato: un
  **link** (video, recensione, post o intervista) possibilmente con minutaggio se si tratta di un video lungo. Le PR che
  aggiungono dischi senza link verificabile vengono chiuse automaticamente.
- **Piccole modifiche.** Tieni le modifiche piccole e focalizzate. Non si accettano PR che
  mischiano aggiunte di dischi, modifiche al codice e refactor nello stesso
  diff.
- **Rigenera i dati, non modificarli a mano.** Modifica solo
  `data/disco_del_giorno.txt` e rigenera con `python3 scripts/parse.py`. Non
  editare a mano `albums.json` / `albums.js` / `covers.*`: sono file generati.
- **Niente duplicati.** Controlla che il disco non sia già presente prima di
  aggiungerlo.
- **Rispetta i formati.** Una riga per disco, `Titolo (anno) - Artista` oppure
  `Artista - Titolo (anno)`. Verifica il parsing prima di aprire la PR.
- **Descrivi la PR.** Spiega cosa cambi e perché; per i dischi includi il link
  alla fonte direttamente nella descrizione.
- **Nessun cambio di scopo.** Resta un progetto statico, non ufficiale e non
  commerciale: niente dipendenze, tracker o chiamate API a runtime.

## Licenza

Codice sotto licenza [MIT](LICENSE). I titoli dei dischi e i nomi degli artisti
appartengono ai rispettivi proprietari.
