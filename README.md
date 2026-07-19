# roza-tg

Multi-bot Telegram controller. Run every bot from one process on a VPS (e.g. justrunmy.app).

## Quick start

```bash
git clone https://github.com/YOUR_USERNAME/roza-tg.git
cd roza-tg
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # then fill in tokens and channel links
python mainControllerBot.py
```

## Project layout

```
roza-tg/
├── mainControllerBot.py   # starts all bots
├── bot.py                 # alias for mainControllerBot
├── .env                   # secrets (not committed)
├── shared/
│   ├── bot_runner.py      # discovery, import, threading
│   ├── bot_base.py        # helpers for building apps
│   └── templates.py       # $VAR$ substitution in response files
└── bots/
    └── yourbot/
        ├── bot.py         # custom workflow (required)
        ├── config.json    # token + env mapping
        ├── response_start.txt
        └── response_handleMessage.txt
```

## Per-bot workflow

Each bot folder **must** have a `bot.py` with:

```python
from pathlib import Path
from shared.bot_base import create_app, get_token, register_text_handlers
from shared.templates import resolve_substitutions

def build_application(bot_dir: Path, config: dict):
    token = get_token(config)
    variables = resolve_substitutions(config)

    app = create_app(token, config["name"])
    register_text_handlers(app, bot_dir, variables)

    # Your custom commands/handlers here
    return app
```

Replace `register_text_handlers` entirely if a bot needs a fully custom flow.

## Template variables

In response `.txt` files, use placeholders like `$CHANNEL_LINK$`.

Map them in `config.json`:

```json
{
  "name": "mybot",
  "token_env": "BOT_TOKEN_1",
  "substitutions": {
    "CHANNEL_LINK": "CHANNEL_LINK_1"
  },
  "env_vars": ["CHANNEL_LINK_1"]
}
```

You can also use env vars directly: `$CHANNEL_LINK_2$` reads from `.env`.

## Add a new bot

1. Add `BOT_TOKEN_N` and `CHANNEL_LINK_N` to `.env`
2. Create `bots/newbotname/` with `bot.py`, `config.json`, and response files
3. Restart `mainControllerBot.py` — new folders are auto-discovered

## Run on VPS

Set `PYTHONUNBUFFERED=1` in `.env` (already in `.env.example`) and run:

```bash
python mainControllerBot.py
```

One thread per bot; all share one process.
