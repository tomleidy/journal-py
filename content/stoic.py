"""Stoic content functions for managing daily stoic prompts"""
import json
import math
import csv
from datetime import datetime, timedelta
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


def stoic_json_set_progress(progress):
    """Save progress if applicable"""
    state = get_state()
    current_date = datetime.now().date()
    saved_date = progress['updated_on'].date()

    if current_date != saved_date:
        new_progress = {
            "day": progress['day'],
            "updated_on": datetime.now().strftime('%Y-%m-%d')
        }
        if state.args['test']:
            print("json.dump:", new_progress)
            return
        with open(STOIC_PROGRESS, 'w', encoding='utf-8') as file:
            json.dump(new_progress, file)


def get_number_of_entries_to_load(progress_day: int) -> int:
    """Return the number of entries to load based on progress relative to current date, within bounds of catchup rate"""
    if progress_day > 366:
        progress_day = ((progress_day - 1) % 366) + 1
    today = datetime.now().timetuple().tm_yday
    if today < progress_day < today + STOIC_CATCHUP_RATE:
        return progress_day - today
    if today == progress_day:
        return 1
    return STOIC_CATCHUP_RATE


def get_stoic_entries() -> str:
    """Return the relevant entry from stoics.csv"""
    progress = stoic_json_get_progress()

    with open(STOIC_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        entries = list(reader)

    num_entries_to_load = get_number_of_entries_to_load(progress['day'])
    result = "\n"

    for x in range(num_entries_to_load):
        day = ((progress['day'] + x - 1) % 366) + 1  # to avoid Dec 31st breakage
        day_entries = [e for e in entries if int(e['Day']) == day]
        entry = day_entries[0] if day_entries else None

        if entry:
            date = datetime.strptime(entry['Date'], '%m/%d')
            text = entry['Question']
        else:
            date = datetime.now()  # Fallback date
            text = f"No entry for day {day}."

        result += f"- Daily Stoic Prompt, {date.strftime('%-m/%d')}:\n{text}\n"
        result += "\t- Morning:\n\t\t- \n\t- Evening:\n\t\t- \n"

    progress['day'] += num_entries_to_load
    stoic_json_set_progress(progress)
    return result
