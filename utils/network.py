"""Network utilities module"""

import time
import json
from pathlib import Path
from typing import Optional, Tuple, Dict
import netifaces
import requests


def debug_print(msg: str, start_time: float):
    """Print debug timing information."""
    # TODO: Implement debug printing command line option
    # print(f"{msg}: {time.time() - start_time:.2f}s")


def get_network_addresses() -> Tuple[Optional[str], Optional[str]]:
    """Get current IPv4 and IPv6 addresses for the active network interface."""
    try:
        gateways = netifaces.gateways()
        if "default" not in gateways or netifaces.AF_INET not in gateways["default"]:
            return None, None

        default_interface = gateways["default"][netifaces.AF_INET][1]
        addrs = netifaces.ifaddresses(default_interface)

        # Get IPv4 address
        ipv4 = None
        if netifaces.AF_INET in addrs:
            ipv4 = addrs[netifaces.AF_INET][0]["addr"]

        # Get IPv6 address
        ipv6 = None
        if netifaces.AF_INET6 in addrs:
            # Filter out link-local addresses
            global_ipv6s = [
                addr["addr"].split("%")[0]
                for addr in addrs[netifaces.AF_INET6]
                if not addr["addr"].startswith("fe80:")
            ]
            if global_ipv6s:
                ipv6 = global_ipv6s[0]
        return ipv4, ipv6
    except (KeyError, netifaces.NetifacesError, OSError) as e:
        print(f"Error getting network addresses: {e}")
        return None, None


class NetworkLocation:
    """Network location class to store IP addresses and coordinates."""

    def __init__(
        self,
        ipv4: Optional[str] = None,
        ipv6: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        zipcode: Optional[str] = None,
    ):
        self.ipv4 = ipv4
        self.ipv6 = ipv6
        self.latitude = latitude
        self.longitude = longitude
        self.zipcode = zipcode

    def to_dict(self) -> dict:
        """Convert object to dictionary."""
        return {
            "ipv4": self.ipv4,
            "ipv6": self.ipv6,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "zipcode": self.zipcode,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "NetworkLocation":
        """Create object from dictionary."""
        return cls(
            ipv4=data.get("ipv4"),
            ipv6=data.get("ipv6"),
            latitude=data.get("latitude"),
            longitude=data.get("longitude"),
            zipcode=data.get("zipcode"),
        )


def load_network_cache() -> Dict[str, NetworkLocation]:
    """Load saved network location data from JSON file."""
    cache_path = Path("network_cache.json")
    if cache_path.exists():
        with open(cache_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return {k: NetworkLocation.from_dict(v) for k, v in data.items()}
    return {}


def save_network_cache(cache: Dict[str, NetworkLocation]) -> None:
    """Save network location data to JSON file."""
    with open("network_cache.json", "w", encoding="utf-8") as f:
        json.dump({k: v.to_dict() for k, v in cache.items()}, f, indent=2)


def get_lat_lon_from_zip(zipcode: str) -> Dict[str, float]:
    """Convert ZIP code to latitude/longitude using public API."""
    try:
        response = requests.get(f"https://api.zippopotam.us/us/{zipcode}", timeout=5)
        if response.status_code == 404:
            raise ValueError(f"ZIP code not found: {zipcode}")
        response.raise_for_status()

        data = response.json()
        return {
            "zipcode": zipcode,
            "latitude": float(data["places"][0]["latitude"]),
            "longitude": float(data["places"][0]["longitude"]),
        }
    except requests.RequestException as e:
        raise RuntimeError(f"Could not look up coordinates for ZIP {zipcode}: {e}")


def create_network_key(ipv4: Optional[str], ipv6: Optional[str]) -> str:
    """Create a unique key for the network based on IP addresses."""
    return f"{ipv4 or 'none'}_{ipv6 or 'none'}"


def get_location() -> Tuple[float, float]:
    """Get location based on network IPs and saved/input location data."""
    start_time = time.time()

    try:
        ipv4, ipv6 = get_network_addresses()
        debug_print("Network detection", start_time)

        if not ipv4 and not ipv6:
            raise ValueError("Location information unavailable: no network detected")

        network_key = create_network_key(ipv4, ipv6)
        network_cache = load_network_cache()
        debug_print("Load cache", start_time)

        if network_key not in network_cache:
            print(f"Network not found in cache (IPv4: {ipv4}, IPv6: {ipv6})")
            try:
                zipcode = input("Enter ZIP code for current network: ")
                location_data = get_lat_lon_from_zip(zipcode)
            except Exception as e:
                raise RuntimeError(
                    "Location information unavailable: lookup failed"
                ) from e

            debug_print("ZIP lookup", start_time)

            network_cache[network_key] = NetworkLocation(
                ipv4=ipv4,
                ipv6=ipv6,
                latitude=location_data["latitude"],
                longitude=location_data["longitude"],
                zipcode=zipcode,
            )
            try:
                save_network_cache(network_cache)
                debug_print("Save cache", start_time)
            except Exception:
                pass  # Ignore cache save failures

        location = network_cache[network_key]
        return (location.latitude, location.longitude)

    except Exception as e:
        raise RuntimeError(f"Location information unavailable: {str(e)}")
