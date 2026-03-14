import importlib.resources

import mini_research.prompts as _pkg


def load_prompt(name: str, **vars: str) -> str:
    text = importlib.resources.files(_pkg).joinpath(f"{name}.md").read_text(encoding="utf-8")
    return text.format_map(vars)
