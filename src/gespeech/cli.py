import argparse
import base64
import io
import wave
from typing import Any

import sounddevice
from dotenv import load_dotenv
from google import genai

from gespeech.script import DialogueLine, Script, load_script

load_dotenv()


DEFAULT_REQUEST = {
    "model_id": "gemini-3.8-flash-lite-tts",
    "voice_id": "ja-jp-tutor-1",
    "style": "",
}


def _turn(text: str, speaker: str | None, style: str) -> dict[str, Any]:
    metadata: dict[str, Any] = {"type": "speech_metadata"}
    if speaker:
        metadata["speaker"] = speaker
    if style:
        metadata["style"] = style
    turn: dict[str, Any] = {"type": "text", "text": text}
    if len(metadata) > 1:
        turn["annotations"] = [metadata]
    return turn


def generate_speech(
    text: str,
    dialogue: list[DialogueLine] | None = None,
    speakers: dict[str, str] | None = None,
    **request: Any,
) -> bytes:
    """Generate speech and return WAV bytes (24 kHz, mono, 16-bit PCM).

    Multi-speaker mode is used when `dialogue` and `speakers` are given.
    """
    request = {**DEFAULT_REQUEST, **request}
    style = request["style"]

    if dialogue and speakers:
        content = [_turn(l.text, l.speaker, style) for l in dialogue]
        speech_config: Any = {
            "speakers": [{"speaker": n, "voice": v} for n, v in speakers.items()]
        }
    else:
        content = [_turn(text, None, style)]
        speech_config = [{"voice": request["voice_id"]}]

    # Keep the client referenced: a temporary gets garbage-collected and closes
    # its HTTP client before the request is sent.
    with genai.Client() as client:
        interaction = client.interactions.create(
            model=request["model_id"],
            input=[{"type": "user_input", "content": content}],
            response_format={"type": "audio"},
            generation_config={"speech_config": speech_config},
        )
        return base64.b64decode(interaction.output_audio.data)


def play(wav: bytes) -> None:
    with wave.open(io.BytesIO(wav)) as w:
        with sounddevice.RawOutputStream(
            samplerate=w.getframerate(),
            channels=w.getnchannels(),
            dtype="int16",
        ) as stream:
            stream.write(w.readframes(w.getnframes()))


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate speech using Gemini TTS.")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("-t", "--text", type=str, help="Text to convert to speech")
    source.add_argument(
        "-i", "--input", type=str, help="Input text file to convert to speech"
    )
    parser.add_argument(
        "-p", "--play", action="store_true", help="Play the generated speech"
    )
    parser.add_argument(
        "-o",
        "--outfile",
        type=str,
        help="Output WAV file for the generated speech",
    )

    args = parser.parse_args()

    if not (args.play or args.outfile):
        parser.error("at least one of -p/--play or -o/--outfile is required")

    if args.input:
        try:
            script = load_script(args.input)
        except (OSError, ValueError) as e:
            parser.error(f"{args.input}: {e}")
    else:
        script = Script(text=args.text)

    audio = generate_speech(
        script.text, script.dialogue, script.speakers, **script.request
    )
    if args.outfile:
        with open(args.outfile, "wb") as f:
            f.write(audio)
    if args.play:
        play(audio)
