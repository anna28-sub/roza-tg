import sys
import time
from pathlib import Path

from shared.bot_runner import PROJECT_ROOT, load_env, load_bot_config, start_bot_thread

BOTS_DIR = PROJECT_ROOT / "bots"


def discover_bots() -> list[Path]:
    if not BOTS_DIR.is_dir():
        return []

    bot_dirs = []
    for entry in sorted(BOTS_DIR.iterdir()):
        if entry.is_dir() and (entry / "config.json").is_file() and (entry / "bot.py").is_file():
            bot_dirs.append(entry)
    return bot_dirs


def main():
    load_env()

    bot_dirs = discover_bots()
    if not bot_dirs:
        print(f"No bots found in {BOTS_DIR}/")
        print("Each bot needs its own folder with config.json and bot.py")
        sys.exit(1)

    print(f"Starting {len(bot_dirs)} bot(s)...")
    threads = []

    for bot_dir in bot_dirs:
        config = load_bot_config(bot_dir)
        print(f"  → {config['name']} ({bot_dir.name})")
        threads.append(start_bot_thread(bot_dir))

    print("\nAll bots started. Press Ctrl+C to stop.\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")


if __name__ == "__main__":
    main()
