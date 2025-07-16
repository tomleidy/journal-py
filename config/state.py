"""Runtime state management for the journal application"""

from os import path
from typing import Dict, Any, List
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class JournalState:
    """Central state management for journal application"""

    args: Dict[str, Any]
    current_hour: int
    is_late_night: bool
    is_morning: bool
    is_afternoon: bool
    is_evening: bool
    timestamp_hhmm: str
    title_now: str
    title_now_8_weeks_ago: str
    path: str
    entry_file_path: str
    editor_subprocess: List[str]
    editor_8_weeks_ago_subprocess: List[str]

    @classmethod
    def initialize(cls, args: Dict[str, Any]) -> "JournalState":
        """Create initial state based on current time and arguments"""
        from . import settings
        from utils.dates import generate_title

        current_hour = int(datetime.now().strftime("%H"))
        is_late_night = current_hour < settings.MORNING_START_HOUR
        is_morning = (
            settings.MORNING_START_HOUR < current_hour < settings.AFTERNOON_START_HOUR
        )
        is_afternoon = (
            settings.AFTERNOON_START_HOUR < current_hour < settings.EVENING_START_HOUR
        )
        is_evening = current_hour > settings.EVENING_START_HOUR

        # Get platform-specific settings
        platform_settings = settings.get_platform_settings()

        # Override path if in test mode
        journal_path = (
            path.expanduser("~") if args["test"] else platform_settings["path"]
        )

        # Calculate timestamp
        timestamp_hhmm = (
            str(2400 + current_hour)
            if is_late_night
            else datetime.now().strftime("%H%M")
        )

        # Calculate titles
        base_date = (
            datetime.now() - timedelta(days=1) if is_late_night else datetime.now()
        )
        weeks_ago_date = (
            base_date - timedelta(weeks=8, days=1)
            if is_late_night
            else base_date - timedelta(weeks=8)
        )

        title_now = generate_title(base_date)
        title_now_8_weeks_ago = generate_title(weeks_ago_date)

        # Calculate entry path and editor command
        entry_file_path = f"{journal_path}/{title_now}.txt"
        entry_8_weeks_ago_path = f"{journal_path}/{title_now_8_weeks_ago}.txt"
        editor_subprocess = platform_settings["editor_subprocess"] + [entry_file_path]
        editor_8_weeks_ago_subprocess = platform_settings["editor_subprocess"] + [
            entry_8_weeks_ago_path
        ]
        return JournalState(
            args=args,
            current_hour=current_hour,
            is_late_night=is_late_night,
            is_morning=is_morning,
            is_afternoon=is_afternoon,
            is_evening=is_evening,
            timestamp_hhmm=timestamp_hhmm,
            title_now=title_now,
            title_now_8_weeks_ago=title_now_8_weeks_ago,
            path=journal_path,
            entry_file_path=entry_file_path,
            editor_subprocess=editor_subprocess,
            editor_8_weeks_ago_subprocess=editor_8_weeks_ago_subprocess,
        )


# Global state instance
journal_state = None


def initialize_state(args: Dict[str, Any]) -> None:
    """Initialize the global state"""
    global journal_state  # pylint: disable=global-statement
    journal_state = JournalState.initialize(args)


def get_state() -> JournalState:
    """Get the current state"""
    if journal_state is None:
        raise RuntimeError("Journal state not initialized")
    return journal_state
