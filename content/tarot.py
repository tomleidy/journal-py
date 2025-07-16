"""Tarot content functions"""

import random
import csv
from config.settings import TAROT_CSV, TAROT_SKIP_COLUMNS, TAROT_COLUMN_MAX_LEN


def pull_tarot_card() -> str:
    """Pull a tarot card from the tarot.csv file"""
    with open(TAROT_CSV, "r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))
        card = random.choice(reader)

    result = "Tarot: "
    for column, value in card.items():
        if not isinstance(value, str) or column in TAROT_SKIP_COLUMNS:
            continue
        if len(value) > TAROT_COLUMN_MAX_LEN or value == "":
            continue
        if len(value) > 0 and value[-1] == ".":
            continue
        result += f"{value}, "

    return result[:-2] + "\n"
