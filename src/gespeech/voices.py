import argparse

from dotenv import load_dotenv
from google import genai

load_dotenv()


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "List available Gemini TTS voices.\n\n"
            "Output format:\n"
            "  ID | DISPLAY_NAME (LANGUAGE, ACCENT, GENDER, pitch=PITCH): DESCRIPTION\n\n"
            "ID is the name to use as the voice."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "-l", "--language", action="append", help="BCP-47 language code (repeatable)"
    )
    parser.add_argument(
        "-g", "--gender", action="append", choices=["female", "male", "neutral"]
    )
    parser.add_argument("--pitch", action="append", choices=["low", "medium", "high"])
    parser.add_argument(
        "--type",
        action="append",
        dest="type_",
        choices=["prebuilt", "prompted", "replicated"],
    )
    parser.add_argument("-s", "--search", help="Substring match on name/description")
    args = parser.parse_args()

    filters = {
        "language_code": args.language,
        "gender": args.gender,
        "pitch": args.pitch,
        "type_": args.type_,
        "search": args.search,
    }
    filters = {k: v for k, v in filters.items() if v}

    with genai.Client() as client:
        page_token = None
        while True:
            response = client.voices.list(
                page_size=1000,
                **({"page_token": page_token} if page_token else {}),
                **filters,
            )
            for v in response.voices or []:
                print(
                    f"{v.id} | {v.display_name} ({v.language_code}, {v.accent}, "
                    f"{v.gender}, pitch={v.pitch}): {v.description}"
                )
            page_token = response.next_page_token
            if not page_token:
                break
