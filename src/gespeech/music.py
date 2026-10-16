import argparse
import base64
from pathlib import Path

from dotenv import load_dotenv
from google import genai

load_dotenv()

MODEL = "lyria-3.5"


def generate_music(prompt: str, model: str = MODEL) -> bytes:
    """Generate music from a text prompt and return MP3 bytes."""
    with genai.Client() as client:
        interaction = client.interactions.create(
            model=model, input=prompt, stream=False
        )
    audio = interaction.output_audio
    if not audio:
        raise RuntimeError("no audio was returned")
    return base64.b64decode(audio.data)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate music using Lyria.")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("-t", "--text", help="Prompt describing the music")
    source.add_argument("-i", "--input", help="Text file containing the prompt")
    parser.add_argument(
        "-o",
        "--outfile",
        default="music.mp3",
        help="Output MP3 file (default: %(default)s)",
    )
    parser.add_argument(
        "-m", "--model", default=MODEL, help="Model (default: %(default)s)"
    )
    args = parser.parse_args()

    if args.input:
        try:
            prompt = Path(args.input).read_text(encoding="utf-8")
        except OSError as e:
            parser.error(str(e))
    else:
        prompt = args.text

    try:
        audio = generate_music(prompt, args.model)
    except RuntimeError as e:
        parser.exit(1, f"{parser.prog}: error: {e}\n")
    Path(args.outfile).write_bytes(audio)
