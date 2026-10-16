import argparse
import base64
import mimetypes
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from google import genai

load_dotenv()

MODEL = "gemini-3.8-flash-lite-tts"

# Statements the speaker must recite in the consent audio (verbatim).
CONSENT_STATEMENTS = {
    "ja": "私はこの音声の所有者であり、Googleがこの音声を使用して音声合成モデルを作成することを承認します。",
    "en": "I am the owner of this voice and I consent to Google using this voice to create a synthetic voice model.",
}


def _audio(path: str) -> dict[str, str]:
    mime_type = mimetypes.guess_type(path)[0] or "audio/wav"
    data = base64.b64encode(Path(path).read_bytes()).decode("ascii")
    return {"mime_type": mime_type, "data": data}


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Create a replicated (custom) voice from a reference recording.\n\n"
            "Source audio: 10-30 seconds of clean speech from one adult speaker.\n"
            "Consent audio: the same speaker reciting the consent statement\n"
            "(print it with -l). 24 kHz mono 16-bit WAV is recommended for both."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("-s", "--source", help="Source (reference) audio file")
    parser.add_argument("-c", "--consent", help="Consent audio file")
    parser.add_argument(
        "-v",
        "--voice-id",
        help="Name for the voice (display_name). The ID itself is assigned by "
        "the API and printed on success.",
    )
    parser.add_argument(
        "-l",
        "--language",
        choices=sorted(CONSENT_STATEMENTS),
        help="Print the consent statement in this language and exit "
        "(when given without the other options)",
    )
    args = parser.parse_args()

    if args.language and not (args.source or args.consent or args.voice_id):
        print(CONSENT_STATEMENTS[args.language])
        return

    if not (args.source and args.consent):
        parser.error("-s/--source and -c/--consent are required")

    try:
        source_audio = _audio(args.source)
        consent_audio = _audio(args.consent)
    except OSError as e:
        parser.error(str(e))

    voice: Any = {
        "model": MODEL,
        "type": "replicated",
        "replicated": {"source_audio": source_audio, "consent_audio": consent_audio},
    }
    if args.voice_id:
        voice["display_name"] = args.voice_id

    with genai.Client() as client:
        created = client.voices.create(store=True, voice=voice)
    print(created.id)
