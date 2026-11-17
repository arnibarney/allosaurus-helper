"""CLI-Test: Transkribiert eine WAV-Datei ohne Browser.

Beispiele:
    python scripts/test_recognizer.py audio.wav
    python scripts/test_recognizer.py audio.wav gsw --timestamp
"""

import argparse
import sys
from pathlib import Path

# Projekt-Importe ermöglichen, wenn direkt ausgeführt
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.recognizer import transcribe_wav  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description="Allosaurus IPA-Test")
    parser.add_argument("audio", help="Pfad zur WAV-Datei (16 kHz mono empfohlen)")
    parser.add_argument("language", nargs="?", default="de-CH",
                        help="UI-Sprachcode: de-CH, de-DE, fr-FR, it-IT, en-GB, en-US")
    parser.add_argument("--emit", type=float, default=1.0)
    parser.add_argument("--timestamp", action="store_true")
    args = parser.parse_args()

    audio_path = Path(args.audio)
    if not audio_path.exists():
        sys.exit(f"Datei nicht gefunden: {audio_path}")

    print(f"Lade Modell (erster Aufruf lädt ggf. ~200 MB herunter) ...")
    result = transcribe_wav(audio_path, args.language, emit=args.emit, timestamp=args.timestamp)

    print(f"Sprach-Inventar : {result['lang_id']}")
    print(f"IPA             : {result['ipa']}")
    if result["timestamps"]:
        print("Timestamps:")
        for t in result["timestamps"]:
            print(f"  {t['start']:.3f}s (+{t['duration']:.3f}s)  {t['phone']}")


if __name__ == "__main__":
    main()
