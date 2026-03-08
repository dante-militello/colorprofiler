import json
import os

def _config_path() -> str:
    import sys
    if getattr(sys, "frozen", False):
        base = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "ColorProfiler")
        os.makedirs(base, exist_ok=True)
        return os.path.join(base, "config.json")
    return os.path.join(os.path.dirname(__file__), "config.json")

CONFIG_PATH = _config_path()

_DEFAULT = {
    "active_profile": "Normal",
    "profiles": [
        {"name": "Normal", "gamma": 1.0, "dvc": 0, "hue": 0, "monitor": 0, "hotkey": ""},
    ],
}

def load() -> dict:
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH) as f:
            return json.load(f)
    return dict(_DEFAULT)

def save(config: dict):
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)

def get_profiles(config: dict) -> list:
    return config.get("profiles", [])

def get_active(config: dict) -> dict | None:
    name = config.get("active_profile")
    for p in get_profiles(config):
        if p["name"] == name:
            return p
    profiles = get_profiles(config)
    return profiles[0] if profiles else None

def set_active(config: dict, name: str):
    config["active_profile"] = name

def add_profile(config: dict, profile: dict):
    config.setdefault("profiles", []).append(profile)

def remove_profile(config: dict, name: str):
    config["profiles"] = [p for p in get_profiles(config) if p["name"] != name]

def update_profile(config: dict, old_name: str, updated: dict):
    for i, p in enumerate(get_profiles(config)):
        if p["name"] == old_name:
            config["profiles"][i] = updated
            if config.get("active_profile") == old_name:
                config["active_profile"] = updated["name"]
            return

def get_monitors() -> list[dict]:
    import ctypes
    monitors = []
    def cb(hMon, hDC, lprc, data):
        monitors.append({"index": len(monitors) + 1})
        return 1
    PROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p)
    ctypes.windll.user32.EnumDisplayMonitors(None, None, PROC(cb), 0)
    return monitors
