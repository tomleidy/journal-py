"""Tarot content functions"""
import random
from pandas import read_csv
from config.settings import TAROT_CSV, TAROT_SKIP_COLUMNS, TAROT_COLUMN_MAX_LEN


def pull_tarot_card() -> str:
    """Pull a tarot card from the tarot.csv file"""
    df = read_csv(TAROT_CSV, sep=",")
    card = random.choice(df['Card'])
    row = df[df['Card'] == card]
    row = row.squeeze()
    result = "Tarot: "

    for column, value in row.items():
        if not isinstance(value, str) or column in TAROT_SKIP_COLUMNS:
            continue
        if len(value) > TAROT_COLUMN_MAX_LEN or value == "-" or value[-1] == ".":
            continue
        result += f"{value}, "

    return result[:-2] + "\n"
