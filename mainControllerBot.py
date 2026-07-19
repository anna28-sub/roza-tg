import signal
import sys
import threading
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
    threads: list[threading.Thread] = []
    stop_event = threading.Event()

    for bot_dir in bot_dirs:
        config = load_bot_config(bot_dir)
        print(f"  \u2192 {config['name']} ({bot_dir.name})")
        threads.append(start_bot_thread(bot_dir, stop_event))

    print("\nAll bots started. Press Ctrl+C to stop.\n")

    def request_stop(*_args):
        stop_event.set()

    # signal handlers must be registered in the main thread.
    signal.signal(signal.SIGINT, request_stop)
    signal.signal(signal.SIGTERM, request_stop)

    stop_event.wait()
    print("\nShutting down...")
    for thread in threads:
        thread.join(timeout=10)


if __name__ == "__main__":
    main()
