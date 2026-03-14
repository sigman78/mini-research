import re


def extract_json(text: str) -> str:
    """Extract content of first ```json ... ``` block, or return text as-is."""
    m = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
    return m.group(1) if m else text
