"""Stoic content functions for managing daily stoic prompts"""
import json
import math
from datetime import datetime, timedelta
from pandas import read_csv, to_datetime
from config.settings import STOIC_CSV, STOIC_PROGRESS, STOIC_CATCHUP_RATE
from config.state import get_state

def days_until_catch_up(progress_day: int, catchup_rate: int) -> int:
    today_day_of_year = datetime.now().timetuple().tm_yday
    days_behind = today_day_of_year - progress_day
    return math.ceil(days_behind / catchup_rate)

def date_from_now(days_ahead: int) -> str:
    target_date = datetime.now() + timedelta(days=days_ahead)
    return target_date.strftime("%m/%d")


def stoic_json_get_progress() -> dict:
    """Read progress from JSON file or start from beginning if not found."""
    try:
        with open(STOIC_PROGRESS, 'r', encoding='utf-8') as file:
            progress = json.load(file)
            date = datetime.strptime(progress['updated_on'], '%Y-%m-%d')
            return {"day": progress['day'], "updated_on": date}
    except (FileNotFoundError, KeyError):
        return {"day": 1, "updated_on": datetime(2024, 1, 1)}


def stoic_json_set_progress(progress: dict) -> None:
    """Save progress if applicable"""
    state = get_state()
    if datetime.now().date() != progress['updated_on'].date():
        new_progress = {
            "day": progress['day'],
            "updated_on": datetime.now().strftime('%Y-%m-%d')
        }
        if state.args['test']:
            print("json.dump:", new_progress)
            return
        with open(STOIC_PROGRESS, 'w', encoding='utf-8') as file:
            json.dump(new_progress, file)


def get_stoic_entries() -> str:
    """Return the relevant entry from stoics.csv"""
    progress = stoic_json_get_progress()
    current_day = datetime.now().timetuple().tm_yday

    df = read_csv(STOIC_CSV)
    df['Date'] = to_datetime(df['Date'], format='%m/%d', errors='coerce')
    num_entries_to_load = 1
    current_catchup_date = ""
    days_left = 0
    if progress['day'] < current_day:
        num_entries_to_load = STOIC_CATCHUP_RATE
        days_left = days_until_catch_up(progress['day'], STOIC_CATCHUP_RATE)
        current_catchup_date = date_from_now(days_left)

    result = "\n"
    if days_left > 0:
        result += f"Stoic Prompts remaining: {days_left}, est. {current_catchup_date} \n"
    for x in range(num_entries_to_load):
        day = progress['day'] + x
        entry = {}
        if any(df['Day'] == day):
            entry['date'] = df.loc[df['Day'] == day, 'Date'].iloc[0]
            entry['text'] = df.loc[df['Day'] == day, 'Question'].iloc[0]
        else:
            entry['date'] = ""
            entry['text'] = f"No entry for day {day}."
        result += f"- Daily Stoic Prompt, {entry['date'].strftime('%-m/%d')}:\n{entry['text']}\n"
        result += "\t- Morning:\n\t\t- \n\t- Evening:\n\t\t- \n"

    progress['day'] += num_entries_to_load
    stoic_json_set_progress(progress)
    return result
