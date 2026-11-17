"""Allosaurus-Wrapper: Modell einmal laden, Inventar pro Sprache wählen."""

import tempfile
from pathlib import Path

from allosaurus.app import read_recognizer

# UI-Sprachcode -> Allosaurus/PHOIBLE-ID
# 'ipa' = volles Inventar (~230 Phones), gut als Dialekt-Fallback.
LANG_MAP = {
    "de-CH": ["gsw", "deu", "ipa"],   # Schweizerdeutsch -> PHOIBLE-ID gsw, sonst Deutsch, sonst voll
    "de-DE": ["deu", "ipa"],
    "fr-FR": ["fra", "ipa"],
    "it-IT": ["ita", "ipa"],
    "en-GB": ["eng", "ipa"],
    "en-US": ["eng", "ipa"],
}

_recognizer = None


def get_recognizer():
    """Lädt das Universal-Modell beim ersten Aufruf (Download ~200 MB beim allerersten Mal)."""
    global _recognizer
    if _recognizer is None:
        _recognizer = read_recognizer()
    return _recognizer


def resolve_lang_id(ui_lang: str) -> str:
    """Erste verfügbare Allosaurus-Sprach-ID für den UI-Code zurückgeben."""
    rec = get_recognizer()
    for lang_id in LANG_MAP.get(ui_lang, ["ipa"]):
        try:
            if rec.is_available(lang_id):
                return lang_id
        except Exception:
            continue
    return "ipa"


def transcribe_wav(wav_path: Path, ui_lang: str, emit: float = 1.0, timestamp: bool = False):
    """Transkribiert eine WAV-Datei (16 kHz mono empfohlen) in IPA-Phones.

    Rückgabe: dict mit phones (Liste von Strings) und optional timestamps.
    """
    rec = get_recognizer()
    lang_id = resolve_lang_id(ui_lang)

    result = rec.recognize(str(wav_path), lang_id=lang_id, emit=emit, timestamp=timestamp)

    phones = []
    timestamps = []
    if timestamp:
        # Format: "start duration phone" pro Zeile
        for line in str(result).strip().splitlines():
            parts = line.split()
            if len(parts) == 3:
                start, dur, phone = parts
                phones.append(phone)
                timestamps.append({"phone": phone, "start": float(start), "duration": float(dur)})
    else:
        phones = str(result).split()

    return {"lang_id": lang_id, "phones": phones, "ipa": " ".join(phones), "timestamps": timestamps if timestamp else None}
