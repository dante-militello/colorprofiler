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
    engine.reset_profile(0)
    _root.quit()
    sys.exit(0)


def _show_splash(root: ctk.CTk):
    splash = ctk.CTkToplevel(root)
    splash.overrideredirect(True)
    splash.configure(fg_color="#0f0f1a")
    splash.attributes("-topmost", True)
    sw = splash.winfo_screenwidth()
    sh = splash.winfo_screenheight()
    w, h = 320, 120
    splash.geometry(f"{w}x{h}+{(sw - w)//2}+{(sh - h)//2}")
    ctk.CTkLabel(
        splash, text="◉  ColorProfiler",
        font=ctk.CTkFont(size=22, weight="bold"),
        text_color="#4fa8ff",
    ).pack(expand=True)
    ctk.CTkLabel(
        splash, text="Iniciando...",
        font=ctk.CTkFont(size=12),
        text_color="#333366",
    ).pack(pady=(0, 16))
    root.after(2000, splash.destroy)


def main():
    global _config, _root, _botonera, _tray

    _config = prof.load()
    _root = ctk.CTk()
    _root.withdraw()
    _show_splash(_root)

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
