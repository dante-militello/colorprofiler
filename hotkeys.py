import keyboard

_registered: list[str] = []

def register(profiles: list, on_activate):
    clear()
    for p in profiles:
        hk = p.get("hotkey", "").strip()
        if hk:
            try:
                keyboard.add_hotkey(hk, on_activate, args=(p,))
                _registered.append(hk)
            except Exception:
                pass

def clear():
    for hk in _registered:
        try:
            keyboard.remove_hotkey(hk)
        except Exception:
            pass
    _registered.clear()
