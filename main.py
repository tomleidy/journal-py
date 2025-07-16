"""Entry point for journal templating script"""

import argparse
from os import path
from config.state import initialize_state, get_state
from writer.entry import (
    create_morning_content,
    create_entry,
    update_entry_with_new_content,
    get_evening_update_string,
    move_stoics_to_end,
)
from utils.file_ops import open_editor
from content.tarot import pull_tarot_card
from content.questions import get_questions_not_in_entry
from content.stoic import get_stoic_entries


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Journal templating script")
    parser.add_argument(
        "-a",
        "--all",
        default=False,
        action="store_true",
        help="add everything (equivalent: -qts)",
    )
    parser.add_argument(
        "-q",
        "--questions",
        default=False,
        action="store_true",
        help="add questions when creating an entry",
    )
    parser.add_argument(
        "-t",
        "--tarot",
        default=False,
        action="store_true",
        help="pull a tarot card and insert it into the entry",
    )
    parser.add_argument(
        "-s",
        "--stoic-prompt",
        default=False,
        action="store_true",
        help="add prompts from stoic CSV file",
    )
    parser.add_argument(
        "-T",
        "--test",
        default=False,
        action="store_true",
        help="run in test mode, create file in ~ instead of normal location",
    )
    parser.add_argument(
        "-M",
        "--do-not-move-stoics",
        default=False,
        action="store_true",
        help="move stoic questions below #EveningPages / end of entry",
    )
    parser.add_argument(
        "-z",
        "--zodiac",
        default=False,
        action="store_true",
        help="add zodiac information to entry",
    )
    parser.add_argument(
        "-N",
        "--no-review",
        default=False,
        help="skip review of entry from 8 weeks ago (even if it exists)",
    )

    args = vars(parser.parse_args())

    if args["all"]:
        args["questions"] = True
        args["tarot"] = True
        # args["zodiac"] = True

    return args


def main():
    """Main entry point"""
    args = parse_arguments()
    initialize_state(args)
    state = get_state()

    if path.exists(state.entry_file_path):
        if state.is_evening or state.is_late_night:
            update_entry_with_new_content(
                get_evening_update_string(), "\n", r"^#EveningPages.*"
            )
            if not state.args["do_not_move_stoics"]:
                move_stoics_to_end()
        if state.args["tarot"]:
            update_entry_with_new_content(pull_tarot_card(), "\n", r"^Tarot:.+$")
        if state.args["questions"]:
            update_entry_with_new_content(get_questions_not_in_entry(), "\n")
        if state.args["stoic_prompt"]:
            update_entry_with_new_content(
                get_stoic_entries(), "\n", r"^- Daily Stoic Prompt,.*"
            )
    else:
        initial_content = create_morning_content()
        if not state.args["no_review"]:
            open_editor(state.editor_8_weeks_ago_subprocess)
        create_entry(initial_content)

    if state.args["test"]:
        return
    open_editor(state.editor_subprocess)


if __name__ == "__main__":
    main()
