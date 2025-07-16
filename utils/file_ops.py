"""File operations module"""

import re
import subprocess


def read_question_file(file_path: str) -> list:
    """Read questions from a file and return as a list"""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.readlines()
    except FileNotFoundError:
        print(f"Warning: Question file not found: {file_path}")
        return []


def get_content_and_cut_dictionary(file_path, start, end_non_inclusive) -> dict:
    start_pattern = rf"({start}.*?)"
    end_pattern = rf"({end_non_inclusive}.*?)"
    cut_section = []
    content = []
    cutting = False
    with open(file_path, "r", encoding="utf-8") as file:
        content_list = file.readlines()
    count = 0
    for line in content_list:
        count += 1
        if not cutting and re.match(start_pattern, line):
            print("Cutting at line " + str(count))
            cutting = True
        if re.match(end_pattern, line):
            cutting = False
        if cutting:
            cut_section.append(line)
        else:
            content.append(line)
    return {"content": "".join(content), "cut": "".join(cut_section)}


def open_editor(cmd: list) -> None:
    print(" ".join(cmd[0:-1]) + f' "{cmd[-1]}"')
    subprocess.run(cmd, check=False)
