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


def run_bot(bot_dir: Path):
    config = load_bot_config(bot_dir)
    bot_name = config["name"]
    app = build_application(bot_dir)

    print(f"✅ [{bot_name}] Bot is running...")
    app.run_polling(drop_pending_updates=True)


def start_bot_thread(bot_dir: Path) -> threading.Thread:
    thread = threading.Thread(
        target=run_bot,
        args=(bot_dir,),
        name=f"bot-{bot_dir.name}",
        daemon=True,
    )
    thread.start()
    return thread
