from pathlib import Path

from shared.bot_base import create_app, get_token, register_text_handlers
from shared.templates import resolve_substitutions


def build_application(bot_dir: Path, config: dict):
    token = get_token(config)
    variables = resolve_substitutions(config)

    app = create_app(token, config["name"])
    register_text_handlers(app, bot_dir, variables)

    # Add custom handlers or commands for this bot below.
    # Example:
    # async def custom_cmd(update, context):
    #     await update.message.reply_text("Empire-only response")
    # app.add_handler(CommandHandler("vip", custom_cmd))

    return app
