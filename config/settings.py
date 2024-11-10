"""Static configuration settings for the journal application"""
from os import path

# Go up one level from config/
SCRIPT_DIR = path.dirname(path.dirname(path.abspath(__file__)))
REFERENCE_DIR = path.expanduser("personal/")

STOICS_FILE = "stoics.csv"
STOICS_PROGRESS_FILE = "stoic_progress.json"
TAROT_FILE = "tarot.csv"
QUESTIONS_DAILY_FILE = "questions-daily.txt"
QUESTIONS_WEEKLY_FILE = "questions-weekly.txt"
QUESTIONS_MONTHLY_FILE = "questions-monthly.txt"


# Full paths
TAROT_CSV = path.join(SCRIPT_DIR, REFERENCE_DIR + TAROT_FILE)
STOIC_CSV = path.join(SCRIPT_DIR, REFERENCE_DIR + STOICS_FILE)
STOIC_PROGRESS = path.join(SCRIPT_DIR, REFERENCE_DIR + STOICS_PROGRESS_FILE)
QUESTIONS_DAILY_TXT = path.join(SCRIPT_DIR, REFERENCE_DIR + QUESTIONS_DAILY_FILE)
QUESTIONS_WEEKLY_TXT = path.join(SCRIPT_DIR, REFERENCE_DIR + QUESTIONS_WEEKLY_FILE)
QUESTIONS_MONTHLY_TXT = path.join(SCRIPT_DIR, REFERENCE_DIR + QUESTIONS_MONTHLY_FILE)

# Application settings
GLOBAL_WORDCOUNT_GOAL = 750
MORNING_START_HOUR = 4
AFTERNOON_START_HOUR = 12
EVENING_START_HOUR = 17
STOIC_CATCHUP_RATE = 2

# Tarot settings
TAROT_SKIP_COLUMNS = {'Group', 'Up', 'Across', 'Down'}
TAROT_COLUMN_MAX_LEN = 30

# Platform-specific settings


def get_platform_settings():
    """Get platform-specific paths and settings"""
    import platform

    if platform.system() == "Darwin":
        return {
            'path': path.expanduser("~/Library/Mobile Documents/27N4MQEA55~pro~writer/Documents/Morning Pages"),
            'editor_subprocess': ["open", "-a", "iA Writer"]
        }
    elif platform.system() == "Windows":
        return {
            'path': path.expanduser("~/iCloudDrive/27N4MQEA55~pro~writer/Morning Pages"),
            'editor_subprocess': [r'C:\Program Files\iA Writer\iAWriter.exe']
        }
    else:
        raise ValueError("This script only meant for macOS (Darwin) and Windows at this time")
