"""Word counting utilities for journal entries"""

import re
from config.state import get_state


def get_ia_writer_style_wordcount_from_string(content: str) -> int:
    content = re.sub(r"- \[[x ]\]", "", content)
    content = re.sub(r"[_:><\/=]", " ", content)
    content = re.sub(r"[A-Za-z]/[A-Za-z]", " ", content)
    content = re.sub(r"(\d)\.(?=\d)", r"\1", content)
    content = re.sub(r"(\S)—(\S)", "\1 \2", content)
    content = re.sub(r"[&—-]", "", content)
    content = re.sub(r"([0-9])’([a-zA-Z])", r"\1 \2", content)
    content = re.sub(r" […\?]", "…", content)
    content = re.sub(r"(\S)[…](\S)", "\1 \2", content)
    content = re.sub(r"([a-zA-Z0-9])\.([a-zA-Z0-9])", r"\1 \2", content)
    content = re.sub(r"[↓↑]", "", content)
    content = re.sub(r"(?:\n\n)(\t[^\t\n]+(?:\n\t[^\t\n]+)*)", "", content)
    return len(content.split())


def get_ia_writer_style_wordcount_from_entry() -> int:
    """Determine word count for current entry, approximating macOS iA Writer word count"""
    state = get_state()
    with open(state.entry_file_path, "r", encoding="utf-8") as file:
        content = file.read()
    return get_ia_writer_style_wordcount_from_string(content)
