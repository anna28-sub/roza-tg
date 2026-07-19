import asyncio
import importlib.util
import json
import threading
from pathlib import Path

from dotenv import load_dotenv
from telegram.ext import Application

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def load_env():
    load_dotenv(PROJECT_ROOT / ".env")


def load_bot_config(bot_dir: Path) -> dict:
    config_path = bot_dir / "config.json"
    with open(config_path, encoding="utf-8") as f:
        return json.load(f)


def load_bot_module(bot_dir: Path):
    bot_file = bot_dir / "bot.py"
    if not bot_file.is_file():
        raise FileNotFoundError(f"Missing bot.py in {bot_dir}")

    module_name = f"bots.{bot_dir.name}.bot"
    spec = importlib.util.spec_from_file_location(module_name, bot_file)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load {bot_file}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build_application(bot_dir: Path) -> Application:
    config = load_bot_config(bot_dir)
    module = load_bot_module(bot_dir)

    if not hasattr(module, "build_application"):
        raise AttributeError(f"{bot_dir / 'bot.py'} must define build_application(bot_dir, config)")

    app = module.build_application(bot_dir, config)
    if not isinstance(app, Application):
        raise TypeError(f"build_application in {bot_dir.name} must return an Application")

    return app


def run_bot(bot_dir: Path, stop_event: threading.Event):
    """Run a single bot in its own thread with a dedicated asyncio loop.

    python-telegram-bot's Application.run_polling() relies on asyncio.run() and
    installs signal handlers, both of which only work in the main thread. When
    launching multiple bots from separate threads, drive each Application
    manually: create a per-thread event loop, then mirror the lifecycle that
    run_polling() uses internally (see PTB source):
      initialize -> updater.start_polling -> start -> run
      -> updater.stop -> stop -> shutdown
    The loop exits when stop_event is signalled by the controller.
    """
    config = load_bot_config(bot_dir)
    bot_name = config["name"]
    app = build_application(bot_dir)
    if app.updater is None:
        raise RuntimeError(f"[{bot_name}] Application has no Updater; cannot run polling")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def lifecycle():
        await app.initialize()
        await app.updater.start_polling(drop_pending_updates=True)
        await app.start()
        print(f"\u2705 [{bot_name}] Bot is running...")
        try:
            while not stop_event.is_set():
                await asyncio.sleep(0.25)
        finally:
            await app.updater.stop()
            await app.stop()
            await app.shutdown()

    try:
        loop.run_until_complete(lifecycle())
    except KeyboardInterrupt:
        stop_event.set()
        loop.run_until_complete(lifecycle())
    finally:
        loop.close()


def start_bot_thread(bot_dir: Path, stop_event: threading.Event) -> threading.Thread:
    thread = threading.Thread(
        target=run_bot,
        args=(bot_dir, stop_event),
        name=f"bot-{bot_dir.name}",
        daemon=True,
    )
    thread.start()
    return thread
