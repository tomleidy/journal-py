"""Entry module for journal writing operations"""
import re
from config.state import get_state
from config.settings import GLOBAL_WORDCOUNT_GOAL
from utils.file_ops import get_content_and_cut_dictionary
from writer.wordcount import get_ia_writer_style_wordcount_from_string, get_ia_writer_style_wordcount_from_entry
from content.tarot import pull_tarot_card
from content.stoic import get_stoic_entries
from content.questions import get_questions_not_in_entry


def create_morning_content() -> str:
    """Create initial morning journal content"""
    state = get_state()
    initial_content = f"""{state.title_now}\n"""
    initial_content += f"""#MorningPages, started at {state.timestamp_hhmm}\n"""
    initial_content += "\n\n\nGoal WC: MORNINGWORDCOUNT\n"
    if state.args['tarot']:
        initial_content += f"{pull_tarot_card()}\n"
    if state.args['questions']:
        initial_content += get_questions_not_in_entry()
    if state.args['stoic_prompt']:
        initial_content += get_stoic_entries()
    current_wc = get_ia_writer_style_wordcount_from_string(initial_content)
    goal_wc = current_wc + GLOBAL_WORDCOUNT_GOAL
    initial_content = initial_content.replace("MORNINGWORDCOUNT", str(goal_wc))
    return initial_content


def create_entry(content: str) -> None:
    """Create a new journal entry"""
    state = get_state()
    if state.args['test']:
        print(content)
        return
    with open(state.entry_file_path, 'w', encoding='utf-8') as file:
        file.write(content)


def update_entry_with_new_content(new_content: str, expected_ending: str, exclusion_re: str = None) -> None:
    """Update existing entry with new content"""
    state = get_state()
    content = ""
    with open(state.entry_file_path, "r", encoding="utf-8") as file:
        content = file.read()
    if exclusion_re and re.search(exclusion_re, content, flags=re.MULTILINE):
        return
    if not content.endswith("\n\n"):
        content += expected_ending
    content += new_content
    if state.args['test']:
        print(content)
        return
    with open(state.entry_file_path, "w", encoding="utf-8") as file:
        file.write(content)


def get_evening_update_string() -> str:
    """Generate evening journal update string"""
    state = get_state()
    content = f"\n#EveningPages, started at {state.timestamp_hhmm}\n\n\n\n"
    current_wc = get_ia_writer_style_wordcount_from_string(content)
    current_wc += get_ia_writer_style_wordcount_from_entry()
    goal_wordcount = str(current_wc + GLOBAL_WORDCOUNT_GOAL + 3)
    content += f"Goal WC: {goal_wordcount}"
    return content


def move_stoics_to_end() -> None:
    """Move stoic prompts to end of entry"""
    state = get_state()
    cut_section = get_content_and_cut_dictionary(state.entry_file_path,
                                                 r"^- Daily Stoic Prompt,.*",
                                                 r"^#EveningPages.*")
    with open(state.entry_file_path, 'w', encoding="utf-8") as file:
        file.write(cut_section['content'] + "\n\n")
        file.write(cut_section['cut'])
