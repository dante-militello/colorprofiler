import pystray
from PIL import Image, ImageDraw


def _make_icon() -> Image.Image:
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([4, 4, 60, 60], fill="#2a7fff")
    d.ellipse([18, 18, 46, 46], fill="#1a1a2e")
    d.ellipse([22, 22, 42, 42], fill="#2a7fff")
    return img


class TrayApp:
    def __init__(self, on_left_click, on_quit):
        self.on_left_click = on_left_click
        self.on_quit = on_quit
        self._icon: pystray.Icon | None = None

    def _menu(self) -> pystray.Menu:
        return pystray.Menu(
            pystray.MenuItem("Abrir", lambda _: self.on_left_click(), default=True, visible=False),
            pystray.MenuItem("Abrir panel", lambda _: self.on_left_click()),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Salir", lambda _: self._quit()),
        )

    def _quit(self):
        self._icon.stop()
        self.on_quit()

    def run(self):
        self._icon = pystray.Icon("colorprofiler", _make_icon(), "ColorProfiler", self._menu())
        self._icon.run()
