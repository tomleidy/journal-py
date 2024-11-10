"""Questions content functions"""
import re
from os import path
from config.state import get_state
from config.settings import (
    QUESTIONS_DAILY_TXT,
    QUESTIONS_WEEKLY_TXT,
    QUESTIONS_MONTHLY_TXT
)
from utils.file_ops import read_question_file
from utils.dates import is_sunday, is_first_of_month


def get_questions_not_in_entry() -> str:
    """Get questions from appropriate files based on the date"""
    content = ""
    question_list = []

    # Always read daily questions
    question_list.extend(read_question_file(QUESTIONS_DAILY_TXT))

    # Add weekly questions on Sunday
    if is_sunday():
        question_list.extend(read_question_file(QUESTIONS_WEEKLY_TXT))

    # Add monthly questions on the first of the month
    if is_first_of_month():
        question_list.extend(read_question_file(QUESTIONS_MONTHLY_TXT))

    # Remove questions that are already in the entry
    state = get_state()
    if path.exists(state.entry_file_path):
        with open(state.entry_file_path, "r", encoding='utf-8') as file:
            entry_content = file.readlines()
            for line in entry_content:
                if ":" in line:
                    line = line.split(":")[0] + ":\n"
                if line in question_list:
                    question_list.remove(line)

    content = re.sub(r":\n", ": \n", "".join(question_list), flags=re.MULTILINE)
    return content
