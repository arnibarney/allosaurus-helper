"""FastAPI-Backend: Audio-Upload -> IPA-Transkription via Allosaurus."""

import shutil
import subprocess
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from backend.recognizer import LANG_MAP, transcribe_wav

app = FastAPI(title="IPA-Transkribierer (Allosaurus)")

# Der Frontend-Container läuft separat (file://), daher einfache CORS-Freigabe für lokale Nutzung.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # nur lokal nutzen; bei echtem Betrieb einschränken
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/languages")
def languages():
    return {"languages": list(LANG_MAP.keys())}


@app.post("/api/transcribe")
def transcribe(
    audio: UploadFile = File(...),
    language: str = Form("de-CH"),
    emit: float = Form(1.0),
    timestamp: bool = Form(False),
):
    if language not in LANG_MAP:
        raise HTTPException(400, f"Unbekannte Sprache: {language}")

    if not shutil.which("ffmpeg"):
        raise HTTPException(500, "ffmpeg nicht gefunden. Bitte installieren und im PATH bereitstellen.")

    with tempfile.TemporaryDirectory(prefix="ipa_tool_") as tmp:
        tmp_path = Path(tmp)
        in_path = tmp_path / "input.bin"
        wav_path = tmp_path / "audio.wav"

        # Upload speichern (webm/opus vom MediaRecorder, aber auch wav/mp4 ok)
        with in_path.open("wb") as f:
            shutil.copyfileobj(audio.file, f)
        if in_path.stat().st_size == 0:
            raise HTTPException(400, "Leere Audiodatei")

        # In 16-kHz-Mono-WAV umwandeln (Allosaurus resampelt selbst, aber WAV wird verlangt)
        cmd = [
            "ffmpeg", "-y", "-loglevel", "error",
            "-i", str(in_path),
            "-ac", "1", "-ar", "16000",
            str(wav_path),
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode != 0 or not wav_path.exists():
            raise HTTPException(400, f"Audio-Konvertierung fehlgeschlagen: {proc.stderr[:500]}")

        try:
            result = transcribe_wav(wav_path, language, emit=emit, timestamp=timestamp)
        except Exception as exc:  # Modell-Fehler sauber melden
            raise HTTPException(500, f"Allosaurus-Fehler: {exc}")

    return result
