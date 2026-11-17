# IPA-Transkribierer mit Allosaurus

Gesprochene Wörter akustisch direkt in IPA-Phoneme transkribieren (kein Umweg über
Orthographie), lokal auf deinem Rechner. Backend: Allosaurus (Universal Phone
Recognizer). Frontend: Web-App im Browser, die Audio ans Backend sendet.

## Architektur

```
Browser (Mikrofon, MediaRecorder, webm/opus)
   │  POST /api/transcribe  (multipart audio + language)
   ▼
FastAPI-Backend
   │  ffmpeg: webm → wav (16 kHz, mono)
   ▼
Allosaurus (vortrainiertes Universal-Modell, CTC)
   │  Phone-Inventory der gewählten Sprache
   │  (deu / fra / ita / eng / gsw, Fallback: volles IPA-Inventar)
   ▼
IPA-Phonemfolge → JSON → Browser (editierbar, Wortliste, JSON/CSV-Export)
```

## Voraussetzungen

- Python 3.9+
- `ffmpeg` im PATH (Audio-Konvertierung)
- Ein moderner Browser (Chrome/Edge/Firefox)

## Installation

```bash
cd ipa-allosaurus-tool
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Beim allerersten Transkribieren lädt Allosaurus automatisch das Universal-Modell
(~200 MB) herunter.

## Starten

Wichtig: Alle Befehle aus dem Projektordner (`allosaurus-helper`) ausführen.

Falls `uvicorn: command not found` erscheint, liegt das meist an einer nicht
aktivierten virtuellen Umgebung oder daran, dass pip in ein anderes Python
installiert hat. Starte uvicorn deshalb sicherheitshalber immer über
`python -m uvicorn`:

```bash
# macOS / Linux
source .venv/bin/activate        # Windows: .venv\Scripts\activate
python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
```

Falls dann `No module named uvicorn` kommt, fehlt die Installation in genau
diesem Python:

```bash
python -m pip install -r requirements.txt
python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
```

Läuft der Server, erscheint eine Zeile wie
`Uvicorn running on http://127.0.0.1:8000`.

Dann `frontend/index.html` im Browser öffnen (Doppelklick genügt) und die
Backend-URL oben prüfen (Standard: http://127.0.0.1:8000).

## Komponenten

| Datei | Zweck |
| --- | --- |
| `backend/app.py` | FastAPI: `/api/transcribe`, `/api/languages`, `/api/health` |
| `backend/recognizer.py` | Lädt Allosaurus einmal, wendet Sprach-Inventar an |
| `frontend/index.html` | Web-App: Aufnehmen, IPA anzeigen/korrigieren, Wortliste, Export |
| `scripts/test_recognizer.py` | CLI-Test ohne Browser: `python scripts/test_recognizer.py audio.wav gsw` |

## Sprachen und Inventare

Allosaurus nutzt PHOIBLE-Inventare. Die App versucht für Schweizerdeutsch die
ID `gsw`; ist sie im Modell nicht enthalten, fällt sie automatisch auf das
komplette IPA-Inventar (`ipa`) zurück, das alle ~230 Phones kennt und am
besten Dialekt-Variationen abbildet. Du kannst das Inventar jederzeit in
`backend/recognizer.py` (`LANG_MAP`) anpassen.

## Hinweise zur Genauigkeit

- Die Ausgabe ist eine Phone-Sequenz (CTC), keine silbische oder
  Wortgrenzen-Struktur; für Einzelwörter ist das ideal.
- Bei Dialekt lohnt es sich, mit `emit` (Phone-Unterdrückung) zu
  experimentieren: Backend-URL-Parameter `emit=0.8` reduziert "eingeschobene"
  Phones.
- Timestamps: `/api/transcribe?timestamp=true` liefert (phone, start, duration).
