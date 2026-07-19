import os
from pathlib import Path

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from shared.templates import apply_templates, load_response, resolve_substitutions


def get_token(config: dict) -> str:
    token_env = config["token_env"]
    token = os.getenv(token_env)
    if not token:
        raise ValueError(f"Missing env var '{token_env}' for bot '{config['name']}'")
    return token


def default_start_text(variables: dict[str, str]) -> str:
    return apply_templates(
        "Welcome!👠\nJoin our active channel:\n$CHANNEL_LINK$",
        variables,
    )


def default_handle_text(variables: dict[str, str]) -> str:
    return apply_templates(
        "Check out our main channel for updates💋:\n$CHANNEL_LINK$",
        variables,
    )


def register_text_handlers(
    app: Application,
    bot_dir: Path,
    variables: dict[str, str],
    *,
    start_file: str = "response_start.txt",
    handle_file: str = "response_handleMessage.txt",
):
    start_response = load_response(bot_dir, start_file, default_start_text(variables), variables)
    handle_response = load_response(bot_dir, handle_file, default_handle_text(variables), variables)

    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(start_response)

    async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(handle_response)

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))


def create_app(token: str, bot_name: str) -> Application:
    app = Application.builder().token(token).build()
    app.bot_data["bot_name"] = bot_name
    return app
