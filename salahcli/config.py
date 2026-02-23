import json
import os
from pathlib import Path

CONFIG_DIR = Path.home() / ".salahcli"
CONFIG_FILE = CONFIG_DIR / "config.json"

def config_exists() -> bool:
    return CONFIG_FILE.exists()

def load_config() -> dict:
    if not config_exists():
        return {}
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def save_config(lat: float, lon: float, tz: int, method: str) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    config = {
        "lat": lat,
        "lon": lon,
        "tz": tz,
        "method": method
    }
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)
