import argparse

from .brain import Brain


def confirm(action: str) -> bool:
    return input(f"\n⚠️  Jarvis wants to run: {action}\n   Allow? [y/N] ").strip().lower() == "y"


def main() -> None:
    parser = argparse.ArgumentParser(prog="jarvis")
    parser.add_argument("--voice", action="store_true", help="hands-free voice mode")
    args = parser.parse_args()

    if args.voice:
        from .voice import run_voice

        run_voice()
        return

    brain = Brain(confirm=confirm)
    print("Jarvis online. Type 'exit' to quit.")
    while True:
        try:
            text = input("\nyou > ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if text.lower() in {"exit", "quit"}:
            break
        if text:
            print(f"\njarvis > {brain.ask(text)}")


if __name__ == "__main__":
    main()
