import ctypes
import os
import subprocess
import tempfile

def _base_dir() -> str:
    import sys
    return sys._MEIPASS if getattr(sys, "frozen", False) else os.path.dirname(__file__)

DISPWIN = os.path.join(_base_dir(), "dispwin.exe")

# ── Gamma via dispwin ─────────────────────────────────────────────

def _make_cal(gamma: float) -> str:
    lines = [
        "CAL\n\n",
        'DESCRIPTOR "Custom Gamma"\n',
        'DEVICE_CLASS "DISPLAY"\n',
        'COLOR_REP "RGB"\n\n',
        "NUMBER_OF_FIELDS 4\n",
        "BEGIN_DATA_FORMAT\n",
        "RGB_I RGB_R RGB_G RGB_B\n",
        "END_DATA_FORMAT\n\n",
        "NUMBER_OF_SETS 256\n",
        "BEGIN_DATA\n",
    ]
    for i in range(256):
        x = i / 255.0
        v = x ** (1.0 / gamma) if gamma > 0 else 0.0
        lines.append(f"{x:.6f} {v:.6f} {v:.6f} {v:.6f}\n")
    lines.append("END_DATA\n")
    return "".join(lines)

def _monitor_indices() -> list[int]:
    monitors = []
    def cb(hMon, hDC, lprc, data):
        monitors.append(len(monitors) + 1)
        return 1
    PROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p)
    ctypes.windll.user32.EnumDisplayMonitors(None, None, PROC(cb), 0)
    return monitors or [1]

def _targets(monitor: int) -> list[int]:
    return _monitor_indices() if monitor == 0 else [monitor]

def apply_gamma(gamma: float, monitor: int = 1):
    cal = _make_cal(gamma)
    for m in _targets(monitor):
        path = os.path.join(tempfile.gettempdir(), f"colorprofiler_{m}.cal")
        with open(path, "w") as f:
            f.write(cal)
        subprocess.run([DISPWIN, f"-d{m}", path], capture_output=True,
                       creationflags=subprocess.CREATE_NO_WINDOW)

def reset_gamma(monitor: int = 1):
    for m in _targets(monitor):
        subprocess.run([DISPWIN, f"-d{m}", "-c"], capture_output=True,
                       creationflags=subprocess.CREATE_NO_WINDOW)

# ── DVC + Hue via NVAPI ───────────────────────────────────────────

_ready = False
_get_func = None
_handles: dict[int, ctypes.c_void_p] = {}

def _init() -> bool:
    global _ready, _get_func, _handles
    if _ready:
        return True
    try:
        lib = ctypes.WinDLL("nvapi64.dll")
        qi = lib.nvapi_QueryInterface
        qi.restype = ctypes.c_void_p

        def get_func(fid, restype=ctypes.c_int, *argtypes):
            ptr = qi(ctypes.c_uint(fid))
            if not ptr:
                raise RuntimeError
            return ctypes.CFUNCTYPE(restype, *argtypes)(ptr)

        _get_func = get_func
        if get_func(0x0150E828)() != 0:
            return False

        enum = get_func(0x9ABDD40D, ctypes.c_int, ctypes.c_uint, ctypes.POINTER(ctypes.c_void_p))
        _handles.clear()
        for i in range(8):
            h = ctypes.c_void_p()
            if enum(i, ctypes.byref(h)) != 0:
                break
            _handles[i + 1] = h

        _ready = bool(_handles)
        return _ready
    except Exception:
        return False

def _nvapi_handles(monitor: int) -> list[ctypes.c_void_p]:
    if not _init():
        return []
    if monitor == 0:
        return list(_handles.values())
    h = _handles.get(monitor) or next(iter(_handles.values()), None)
    return [h] if h else []

def apply_dvc(level: int, monitor: int = 1):
    for h in _nvapi_handles(monitor):
        try:
            _get_func(0x172409B4, ctypes.c_int, ctypes.c_void_p, ctypes.c_uint, ctypes.c_int)(
                h, 0, max(0, min(63, level)))
        except Exception:
            pass

def apply_hue(angle: int, monitor: int = 1):
    for h in _nvapi_handles(monitor):
        try:
            _get_func(0x0F5A0F22C, ctypes.c_int, ctypes.c_void_p, ctypes.c_uint, ctypes.c_int)(
                h, 0, int(angle) % 360)
        except Exception:
            pass

# ── Profile helpers ───────────────────────────────────────────────

def apply_profile(profile: dict):
    m = profile.get("monitor", 1)
    apply_gamma(profile.get("gamma", 1.0), m)
    apply_dvc(profile.get("dvc", 0), m)
    apply_hue(profile.get("hue", 0), m)

def reset_profile(monitor: int = 1):
    reset_gamma(monitor)
    apply_dvc(0, monitor)
    apply_hue(0, monitor)
