import sys
import threading
import customtkinter as ctk
import profiles as prof
import engine
import hotkeys
from tray import TrayApp
from gui import Botonera

ctk.set_appearance_mode("dark")

_config: dict = {}
_root: ctk.CTk | None = None
_botonera: Botonera | None = None
_tray: TrayApp | None = None


def activate_profile(profile: dict):
    prof.set_active(_config, profile["name"])
    prof.save(_config)
    engine.apply_profile(profile)
    if _botonera:
        _botonera.refresh()


def reload_hotkeys():
    hotkeys.register(
        prof.get_profiles(_config),
        lambda p: _root.after(0, activate_profile, p),
    )


def toggle_panel():
    _root.after(0, _botonera.toggle)


def quit_app():
    hotkeys.clear()
    _root.quit()
    sys.exit(0)


def main():
    global _config, _root, _botonera, _tray

    _config = prof.load()
    _root = ctk.CTk()
    _root.withdraw()

    active = prof.get_active(_config)
    if active:
        engine.apply_profile(active)

    reload_hotkeys()

    _botonera = Botonera(
        config=_config,
        on_activate=activate_profile,
        on_update=reload_hotkeys,
        on_quit=quit_app,
    )
    _botonera.withdraw()

    _tray = TrayApp(on_left_click=toggle_panel, on_quit=quit_app)
    threading.Thread(target=_tray.run, daemon=True).start()

    _root.mainloop()


if __name__ == "__main__":
    main()
