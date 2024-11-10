"""Astrological content module"""
from datetime import datetime, timezone, timedelta
from typing import Dict
import time
import ephem
from utils.network import debug_print, get_location


def get_astrology_summary() -> str:
    """Get a formatted string of current astrological information"""
    try:
        content = "\nAstrology:\n"
        status = get_planetary_status()
        content += f"Moon Phase: {get_moon_phase()}\n"

        for planet, info in status.items():
            content += f"{planet} in {info['zodiac']} ({info['motion']}), "
            content += f"↑ {info['rise']}, ↓ {info['set']}\n"

        return content + "\n"
    except Exception:
        return "\nAstrology: Location information unavailable\n"


def get_zodiac_sign(ra_radians: float) -> str:
    """Convert right ascension to zodiac sign."""
    signs = [
        (0, "Aries"), (30, "Taurus"), (60, "Gemini"),
        (90, "Cancer"), (120, "Leo"), (150, "Virgo"),
        (180, "Libra"), (210, "Scorpio"), (240, "Sagittarius"),
        (270, "Capricorn"), (300, "Aquarius"), (330, "Pisces"), (360, "Aries")
    ]
    ra_degrees = (ra_radians * 180 / ephem.pi + 180) % 360
    for i in range(len(signs) - 1):
        if signs[i][0] <= ra_degrees < signs[i + 1][0]:
            return signs[i][1]
    return "Unknown"


def format_time(date: ephem.Date) -> str:
    """Format ephem.Date to local 24-hour time string."""
    # Convert ephem.Date (UTC) to datetime
    utc_dt = ephem.Date(date).datetime()
    # Add UTC timezone info
    utc_dt = utc_dt.replace(tzinfo=timezone.utc)
    # Convert to local time
    local_dt = utc_dt.astimezone()
    return local_dt.strftime("%H:%M")


def get_moon_phase() -> str:
    """Get current moon phase and percentage."""
    moon = ephem.Moon()
    moon.compute()
    phase_percent = moon.phase
    previous_new = ephem.previous_new_moon(ephem.now())
    next_new = ephem.next_new_moon(ephem.now())
    next_full = ephem.next_full_moon(ephem.now())
    previous_full = ephem.previous_full_moon(ephem.now())

    if abs(ephem.now() - previous_new) < 2:
        phase = "New Moon"
    elif abs(ephem.now() - next_full) < 2:
        phase = "Full Moon"
    elif ephem.now() > previous_new and ephem.now() < next_full:
        phase = "Waxing"
        if phase_percent < 50:
            phase += " Crescent"
        else:
            phase += " Gibbous"
    else:
        phase = "Waning"
        if phase_percent < 50:
            phase += " Crescent"
        else:
            phase += " Gibbous"
    return f"{phase} ({phase_percent:.1f}%)"


def is_retrograde(planet, observer, time_period_days=7):
    """Check if a planet is retrograde."""
    now = ephem.now()
    planet.compute(observer)
    current_ra = planet.a_ra

    past_time = now - time_period_days
    planet.compute(past_time)
    past_ra = planet.a_ra

    return past_ra > current_ra


def get_planetary_status() -> Dict[str, Dict]:
    """Get detailed status for all planets."""
    start_time = time.time()

    lat, lon = get_location()
    debug_print("Location lookup", start_time)

    # Get local timezone from system
    local_tz = datetime.now().astimezone().tzinfo

    observer = ephem.Observer()
    observer.lat = str(lat)
    observer.lon = str(lon)
    # Use local time for observer
    observer.date = ephem.Date(datetime.now())
    observer.pressure = 0  # Disable atmospheric refraction
    observer.elevation = 0
    observer.horizon = '-0:34'

    # pylint: disable=no-member
    planets = {
        "Sun": ephem.Sun(),
        "Moon": ephem.Moon(),
        "Mercury": ephem.Mercury(),
        "Venus": ephem.Venus(),
        "Mars": ephem.Mars(),
        "Jupiter": ephem.Jupiter(),
        "Saturn": ephem.Saturn(),
        "Uranus": ephem.Uranus(),
        "Neptune": ephem.Neptune(),
        "Pluto": ephem.Pluto()
    }
    # pylint: enable=no-member

    status = {}
    for name, planet in planets.items():
        planet.compute(observer)

        try:
            next_rise = observer.next_rising(planet)
            rise_time = format_time(next_rise)
        except (ephem.CircumpolarError, ephem.AlwaysUpError):
            rise_time = "∞"

        try:
            next_set = observer.next_setting(planet)
            set_time = format_time(next_set)
        except (ephem.CircumpolarError, ephem.AlwaysUpError):
            set_time = "∞"

        status[name] = {
            "motion": "D" if not is_retrograde(planet, observer) else "R",
            "zodiac": get_zodiac_sign(planet.ra),
            "rise": rise_time,
            "set": set_time
        }

    debug_print("Planetary calculations", start_time)
    return status
