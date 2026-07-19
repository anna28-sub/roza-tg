import os
import re

TEMPLATE_PATTERN = re.compile(r"\$([A-Z_][A-Z0-9_]*)\$")


def resolve_substitutions(config: dict) -> dict[str, str]:
    values: dict[str, str] = {}

    for template_key, env_key in config.get("substitutions", {}).items():
        value = os.getenv(env_key, "")
        if value:
            values[template_key] = value

    for env_key in config.get("env_vars", []):
        value = os.getenv(env_key, "")
        if value:
            values[env_key] = value

    return values


def apply_templates(text: str, variables: dict[str, str]) -> str:
    def replace(match: re.Match) -> str:
        key = match.group(1)
        if key in variables:
            return variables[key]
        env_value = os.getenv(key)
        if env_value is not None:
            return env_value
        return match.group(0)

    return TEMPLATE_PATTERN.sub(replace, text)


def load_response(bot_dir, filename: str, default_text: str, variables: dict[str, str]) -> str:
    filepath = bot_dir / filename
    try:
        with open(filepath, encoding="utf-8") as f:
            text = f.read().strip()
    except FileNotFoundError:
        text = default_text

    return apply_templates(text, variables)
