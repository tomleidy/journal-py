"""Astrological content module"""
from datetime import datetime, timezone
import ephem

# Remove network dependency by providing default test coordinates
DEFAULT_LAT = 40.7128  # New York City
DEFAULT_LON = -74.0060


def get_zodiac_sign(body: ephem.Body) -> str:
    """Get zodiac sign for a celestial body using ecliptic longitude"""
    # Get ecliptic longitude in degrees
    ecl_lon = ephem.Ecliptic(body).lon * 180 / ephem.pi

    # Define zodiac signs and their starting degrees
    signs = [
        (0, "Aries"), (30, "Taurus"), (60, "Gemini"), (90, "Cancer"),
        (120, "Leo"), (150, "Virgo"), (180, "Libra"), (210, "Scorpio"),
        (240, "Sagittarius"), (270, "Capricorn"), (300, "Aquarius"), (330, "Pisces")
    ]

    # Find the appropriate sign
    for deg, sign in signs:
        next_deg = (deg + 30) % 360
        if deg <= ecl_lon < next_deg:
            return sign
    return "Pisces"  # For 330-360 degrees


def format_time(date: ephem.Date) -> str:
    """Format ephem.Date to local 24-hour time string."""
    utc_dt = ephem.Date(date).datetime()
    utc_dt = utc_dt.replace(tzinfo=timezone.utc)
    local_dt = utc_dt.astimezone()
    return local_dt.strftime("%H:%M")


def get_moon_phase() -> str:
    """Get current moon phase and percentage."""
    moon = ephem.Moon()
    moon.compute()
    phase_percent = moon.phase
    previous_new = ephem.previous_new_moon(ephem.now())
    next_full = ephem.next_full_moon(ephem.now())

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


def get_astrological_positions(lat=DEFAULT_LAT, lon=DEFAULT_LON) -> str:
    """Get formatted string of planetary positions and motions"""
    observer = ephem.Observer()
    observer.lat = str(lat)
    observer.lon = str(lon)
    observer.date = ephem.Date(datetime.now())

    planet_order = [
        "Sun", "Moon", "Mercury", "Venus", "Mars",
        "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"
    ]

    planets = get_ephem_planets()

    content = "\nPlanetary Positions:\n"
    content += f"Moon Phase: {get_moon_phase()}\n"

    # Display in specified order
    for name in planet_order:
        planet = planets[name]
        planet.compute(observer)
        motion = "D" if not is_retrograde(planet, observer) else "R"
        content += f"{name} in {get_zodiac_sign(planet)} ({motion})\n"

    return content


def get_ephem_planets() -> dict:
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
    return planets


def get_rise_set_times(lat=DEFAULT_LAT, lon=DEFAULT_LON) -> str:
    """Get formatted string of rise/set times, sorted by rise time"""
    observer = ephem.Observer()
    observer.lat = str(lat)
    observer.lon = str(lon)
    observer.date = ephem.Date(datetime.now())
    observer.pressure = 0
    observer.elevation = 0
    observer.horizon = '-0:34'

    planets = get_ephem_planets()

    # Collect rise/set times and signs
    rise_set_data = []

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

        # Get sign and take first three letters
        sign = get_zodiac_sign(planet)[:3]

        # Store as tuple for sorting
        rise_set_data.append((name, rise_time, set_time, sign))

    # Sort by rise time (putting "∞" at the end)
    def sort_key(item):
        return ("Z" if item[1] == "∞" else item[1])

    rise_set_data.sort(key=sort_key)

    # Format output
    content = "\nRise and Set Times (sorted by rise time):\n"
    for name, rise, settime, sign in rise_set_data:
        content += f"{name:8} ↑ {rise:5} ↓ {settime:5} {sign:3}\n"

    return content


def get_astrology_summary(lat=DEFAULT_LAT, lon=DEFAULT_LON) -> str:
    """Get a formatted string of current astrological information"""
    try:
        return get_astrological_positions(lat, lon) + get_rise_set_times(lat, lon)
    except (ValueError, TypeError) as e:
        return f"\nAstrology: Error calculating positions - {str(e)}\n"


def main():
    """Run standalone astronomical calculations"""
    print(f"Using coordinates: {DEFAULT_LAT}, {DEFAULT_LON}")
    print(get_astrology_summary())


if __name__ == "__main__":
    main()
