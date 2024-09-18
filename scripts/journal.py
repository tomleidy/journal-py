"""Entry point for journal templating script"""
# pylint: disable=C0116,C0103,W0621

from datetime import datetime, timedelta
import platform
import json
import re
import subprocess
import os

TESTING = False
wordcount_goal = 750
current_hour = int(datetime.now().strftime("%H"))
morning_start_hour = 4
afternoon_start_hour = 12
evening_start_hour = 18
questions_txt = "questions.txt"

is_late_night = current_hour < morning_start_hour
is_morning = morning_start_hour < current_hour < afternoon_start_hour
is_afternoon = afternoon_start_hour < current_hour < evening_start_hour
is_evening = current_hour > evening_start_hour


def get_ia_writer_style_wordcount_from_string(content: str) -> int:
    content = re.sub(r'\- \[.\]', '', content)
    content = re.sub(r'[_:><\/=]', ' ', content)
    content = re.sub(r'[A-Za-z]/[A-Za-z]', ' ', content)
    content = re.sub(r'(\S)—(\S)', '\1 \2', content)
    content = re.sub(r'[&—-]', '', content)
    content = re.sub(r'([0-9])’([a-zA-Z])', r'\1 \2', content)
    content = re.sub(r' […\?]', '…', content)
    content = re.sub(r'(\S)[…](\S)', '\1 \2', content)
    content = re.sub(r'([a-zA-Z0-9])\.([a-zA-Z0-9])', r'\1 \2', content)
    return len(content.split())


def get_ia_writer_style_wordcount_from_file(file_path: str) -> int:
    """Determine word count, approximating macOS iA Writer word count"""
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    return get_ia_writer_style_wordcount_from_string(content)


def get_questions_txt(file_path: str) -> str:
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    content = re.sub(r":\n", ": \n", content, flags=re.MULTILINE)
    return content


ordinal_strings = {
    1: "1st", 2: "2nd", 3: "3rd", 4: "4th", 5: "5th", 6: "6th", 7: "7th", 8: "8th",
    9: "9th", 10: "10th", 11: "11th", 12: "12th", 13: "13th", 14: "14th", 15: "15th",
    16: "16th", 17: "17th", 18: "18th", 19: "19th", 20: "20th", 21: "21st", 22: "22nd",
    23: "23rd", 24: "24th", 25: "25th", 26: "26th", 27: "27th", 28: "28th", 29: "29th",
    30: "30th", 31: "31st"
}


blobby = {}
if is_late_night:
    blobby["timestamp_hhmm"] = str(2400 + int(datetime.now().strftime("%H%M")))
else:
    blobby["timestamp_hhmm"] = datetime.now().strftime("%H%M")


def generate_title(base_date: datetime) -> str:
    """Generates title, format is: "YYYYMMDD Day of the week the DDth of Month"."""
    return base_date.strftime(f"%Y%m%d %A the {ordinal_strings[base_date.day]} of %B")


if is_late_night:
    blobby["title_now"] = generate_title(datetime.now() - timedelta(days=1))
    blobby["title_now_8_weeks_ago"] = generate_title(datetime.now() - timedelta(weeks=8, days=1))
else:
    blobby["title_now"] = generate_title(datetime.now())
    blobby["title_now_8_weeks_ago"] = generate_title(datetime.now() - - timedelta(weeks=8))

cur_os = platform.system()
if cur_os == "Darwin":
    path_string = "~/Library/Mobile Documents/27N4MQEA55~pro~writer/Documents/Morning Pages"
    blobby["path"] = os.path.expanduser(path_string)
    blobby["editor_subprocess"] = ["open", "-a", "iA Writer"]
elif cur_os == "Windows":
    blobby["path"] = os.path.expanduser("~/iCloudDrive/27N4MQEA55~pro~writer/Morning Pages")
    blobby["editor_subprocess"] = [r"C:\Program Files\iA Writer\iAWriter.exe"]
else:
    raise ValueError("This script only meant for macOS (Darwin) and Windows at this time")

blobby["questions_file_path"] = blobby["path"] + "/" + questions_txt
if TESTING:
    blobby["path"] = os.path.expanduser("~")
blobby["entry_file_path"] = blobby["path"] + "/" + blobby["title_now"] + ".txt"
blobby["editor_subprocess"].append(blobby["entry_file_path"])


def create_content() -> None:
    initial_content = f"""{blobby["title_now"]}\n"""
    initial_content += f"""#MorningPages, started at {blobby["timestamp_hhmm"]}\n"""
    initial_content += "\n\n\n"
    initial_content += "Goal WC: MORNINGWORDCOUNT\n\n"
    initial_content += get_questions_txt(blobby["questions_file_path"])
    if is_evening is False or is_late_night is False:
        initial_content += "\n"
        initial_content += "#EveningPages, started at EVENINGSTARTTIME"
        initial_content += "\n\n\n"
        initial_content += "Goal WC: EVENINGWORDCOUNT"
    blobby["wordcount_current"] = get_ia_writer_style_wordcount_from_string(initial_content)
    blobby["wordcount_current_plus_goal"] = blobby["wordcount_current"] + wordcount_goal
    old_string = "MORNINGWORDCOUNT"
    new_string = str(blobby["wordcount_current_plus_goal"])
    initial_content = initial_content.replace(old_string, new_string)
    return initial_content


def create_entry(entry_file_path: str, content: str) -> None:
    with open(entry_file_path, 'w', encoding='utf-8') as file:
        file.write(content)


def open_editor(cmd: list) -> None:
    print(" ".join(cmd[0:-1]) + f" \"{cmd[-1]}\"")
    subprocess.run(cmd, check=False)


def update_entry(entry_file_path: str) -> None:
    if is_evening or is_late_night:
        with open(entry_file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            current_wc = get_ia_writer_style_wordcount_from_string(content)
            old_string = "EVENINGWORDCOUNT"
            new_string = str(current_wc + 750)
            content = content.replace(old_string, new_string)
            old_string = "EVENINGSTARTTIME"
            new_string = blobby["timestamp_hhmm"]
            content = content.replace(old_string, new_string)
        with open(entry_file_path, 'w', encoding="utf8") as file:
            file.write(content)


if os.path.exists(blobby["entry_file_path"]):
    if is_evening or is_late_night:
        update_entry(blobby["entry_file_path"])
else:
    initial_content = create_content()
    create_entry(blobby["entry_file_path"], initial_content)


open_editor(blobby["editor_subprocess"])

if TESTING:
    # print(json.dumps(blobby, indent=4, sort_keys=True))
    print("safe to delete file? if not, hit ctrl-C")
    input()
    print("removing " + blobby["entry_file_path"])
    os.remove(blobby["entry_file_path"])