import customtkinter as ctk
from tkinter import messagebox
import profiles as prof
import engine

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class Botonera(ctk.CTkToplevel):
    def __init__(self, config: dict, on_activate, on_update, on_quit):
        super().__init__()
        self.overrideredirect(True)          # quita titlebar nativa
        self.configure(fg_color="#0f0f1a")
        self.resizable(False, False)
        self.config_data = config
        self.on_activate = on_activate
        self.on_update = on_update
        self.on_quit = on_quit
        self._selected = None
        self._saved_values = {}              # referencia para dirty check
        self._drag_x = self._drag_y = 0
        self._build()
        self._position_near_tray()
        self.attributes("-topmost", True)

    # ──────────────────────────── BUILD ───────────────────────────

    def _build(self):
        # ── Header (arrastratable) ──
        header = ctk.CTkFrame(self, fg_color="#12122a", corner_radius=0, height=44)
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(
            header, text="◉  ColorProfiler",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#4fa8ff"
        ).pack(side="left", padx=14)

        ctk.CTkButton(
            header, text="✕", width=36, height=36,
            fg_color="transparent", hover_color="#3a1515",
            text_color="#666", font=ctk.CTkFont(size=14),
            command=self.withdraw
        ).pack(side="right", padx=6, pady=4)

        # Drag support on header
        header.bind("<ButtonPress-1>",   self._drag_start)
        header.bind("<B1-Motion>",       self._drag_move)
        for child in header.winfo_children():
            child.bind("<ButtonPress-1>", self._drag_start)
            child.bind("<B1-Motion>",     self._drag_move)

        # ── Body ──
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True)

        self._left = ctk.CTkFrame(body, fg_color="#0f0f1a", width=165, corner_radius=0)
        self._left.pack(side="left", fill="y", padx=(10, 0), pady=10)
        self._left.pack_propagate(False)

        ctk.CTkFrame(body, fg_color="#1e1e3a", width=1).pack(side="left", fill="y", pady=10)

        self._right = ctk.CTkFrame(body, fg_color="transparent")
        self._right.pack(side="left", fill="both", expand=True, padx=16, pady=12)

        self._build_editor()
        self._refresh_list()

        active = prof.get_active(self.config_data)
        if active:
            self._select(active["name"])

        # ── Footer ──
        ctk.CTkLabel(
            self, text="Hecho con amor por Claude  ·  comandado por Dantezor  ·  vibecodeado en 2hs",
            font=ctk.CTkFont(size=10),
            text_color="#2a2a4a",
        ).pack(pady=(0, 6))

    # ──────────────────────── DRAG ────────────────────────────────

    def _drag_start(self, e):
        self._drag_x = e.x_root - self.winfo_x()
        self._drag_y = e.y_root - self.winfo_y()

    def _drag_move(self, e):
        self.geometry(f"+{e.x_root - self._drag_x}+{e.y_root - self._drag_y}")

    # ─────────────────────── PROFILE LIST ─────────────────────────

    def _refresh_list(self):
        for w in self._left.winfo_children():
            w.destroy()

        ctk.CTkLabel(
            self._left, text="PERFILES",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="#444"
        ).pack(anchor="w", padx=10, pady=(8, 4))

        active_name = self.config_data.get("active_profile")
        for p in prof.get_profiles(self.config_data):
            name = p["name"]
            is_active   = name == active_name
            is_selected = name == self._selected
            ctk.CTkButton(
                self._left,
                text=("▶ " if is_active else "   ") + name,
                anchor="w", width=148, height=34,
                fg_color="#1a3a5c" if is_selected else "#161626",
                hover_color="#1a3a5c",
                border_color="#2a7fff" if is_active else ("#3a5a8a" if is_selected else "#1e1e3a"),
                border_width=1, corner_radius=6,
                font=ctk.CTkFont(size=12),
                text_color="#ffffff" if (is_active or is_selected) else "#999999",
                command=lambda n=name: self._select(n),
            ).pack(pady=2, padx=6, fill="x")

        ctk.CTkFrame(self._left, fg_color="#1e1e3a", height=1).pack(fill="x", padx=6, pady=6)
        ctk.CTkButton(
            self._left, text="＋  Nuevo perfil",
            anchor="w", width=148, height=32,
            fg_color="transparent", hover_color="#1a2a1a",
            border_color="#2a4a2a", border_width=1,
            corner_radius=6, font=ctk.CTkFont(size=12),
            text_color="#4a9a4a",
            command=self._add_profile,
        ).pack(pady=2, padx=6, fill="x")

    # ─────────────────────────── EDITOR ───────────────────────────

    def _build_editor(self):
        r = self._right

        def lbl(text, row_idx):
            ctk.CTkLabel(r, text=text, font=ctk.CTkFont(size=12),
                         text_color="#666", width=72, anchor="w"
                         ).grid(row=row_idx, column=0, sticky="w", pady=4)

        # Nombre
        lbl("Nombre", 0)
        self._name_var = ctk.StringVar()
        self._name_var.trace_add("write", lambda *_: self._mark_dirty())
        ctk.CTkEntry(r, textvariable=self._name_var, width=210,
                     font=ctk.CTkFont(size=13, weight="bold")
                     ).grid(row=0, column=1, columnspan=2, sticky="w", pady=(2, 8))

        # Monitor
        lbl("Monitor", 1)
        monitors = prof.get_monitors()
        self._mon_opts = ["All displays"] + ([f"Display {m['index']}" for m in monitors] or ["Display 1"])
        self._monitor_var = ctk.StringVar(value=self._mon_opts[0])
        self._monitor_var.trace_add("write", lambda *_: self._mark_dirty())
        ctk.CTkOptionMenu(r, variable=self._monitor_var, values=self._mon_opts,
                          width=180, height=30
                          ).grid(row=1, column=1, columnspan=2, sticky="w", pady=4)

        # Gamma
        lbl("Gamma", 2)
        self._gamma_lbl = ctk.CTkLabel(r, text="1.00", width=44,
                                        font=ctk.CTkFont(size=12, weight="bold"),
                                        text_color="#4fa8ff")
        self._gamma_slider = ctk.CTkSlider(r, from_=0.3, to=2.5,
                                            number_of_steps=44, width=200,
                                            command=self._on_gamma)
        self._gamma_slider.grid(row=2, column=1, pady=4, sticky="w")
        self._gamma_lbl.grid(row=2, column=2, padx=6)

        # Vibrance
        lbl("Vibrance", 3)
        self._dvc_lbl = ctk.CTkLabel(r, text="0", width=44,
                                      font=ctk.CTkFont(size=12, weight="bold"),
                                      text_color="#4fa8ff")
        self._dvc_slider = ctk.CTkSlider(r, from_=0, to=63,
                                          number_of_steps=63, width=200,
                                          command=self._on_dvc)
        self._dvc_slider.grid(row=3, column=1, pady=4, sticky="w")
        self._dvc_lbl.grid(row=3, column=2, padx=6)

        # Hue
        lbl("Hue", 4)
        self._hue_lbl = ctk.CTkLabel(r, text="0°", width=44,
                                      font=ctk.CTkFont(size=12, weight="bold"),
                                      text_color="#4fa8ff")
        self._hue_slider = ctk.CTkSlider(r, from_=0, to=359,
                                          number_of_steps=359, width=200,
                                          command=self._on_hue)
        self._hue_slider.grid(row=4, column=1, pady=4, sticky="w")
        self._hue_lbl.grid(row=4, column=2, padx=6)

        # Hotkey
        lbl("Hotkey", 5)
        self._hotkey_var = ctk.StringVar()
        hk_frame = ctk.CTkFrame(r, fg_color="transparent")
        hk_frame.grid(row=5, column=1, columnspan=2, sticky="w", pady=4)
        self._hotkey_display = ctk.CTkLabel(
            hk_frame, textvariable=self._hotkey_var,
            width=140, height=30, anchor="w",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#4fa8ff",
        )
        self._hotkey_display.pack(side="left", padx=(0, 8))
        ctk.CTkButton(
            hk_frame, text="⌨  Asignar", width=90, height=30,
            fg_color="#1a1a2a", hover_color="#2a2a4a",
            border_color="#3a3a6a", border_width=1,
            font=ctk.CTkFont(size=12), text_color="#8888cc",
            command=self._open_hotkey_modal,
        ).pack(side="left", padx=(0, 4))
        ctk.CTkButton(
            hk_frame, text="✕", width=28, height=30,
            fg_color="transparent", hover_color="#3a1515",
            font=ctk.CTkFont(size=12), text_color="#555",
            command=self._clear_hotkey,
        ).pack(side="left")

        # Separator
        ctk.CTkFrame(r, fg_color="#1e1e3a", height=1).grid(
            row=6, column=0, columnspan=3, sticky="ew", pady=10)

        # ── Action buttons ──
        bf = ctk.CTkFrame(r, fg_color="transparent")
        bf.grid(row=7, column=0, columnspan=3, sticky="w")

        # Reset — icono solamente
        ctk.CTkButton(
            bf, text="↺", width=38, height=38,
            font=ctk.CTkFont(size=20),
            fg_color="#1a1a2a", hover_color="#2a2a4a",
            border_color="#3a3a6a", border_width=1,
            text_color="#8888cc",
            command=self._reset,
        ).pack(side="left", padx=(0, 6))

        # Guardar — deshabilitado hasta que haya cambios
        self._save_btn = ctk.CTkButton(
            bf, text="Guardar", width=100, height=38,
            fg_color="#1a3a1a", hover_color="#2a5a2a",
            border_color="#2d6a2d", border_width=1,
            state="disabled",
            command=self._save,
        )
        self._save_btn.pack(side="left", padx=(0, 6))

        # Eliminar — icono solamente
        ctk.CTkButton(
            bf, text="🗑", width=38, height=38,
            font=ctk.CTkFont(size=18),
            fg_color="#1a0f0f", hover_color="#3a1515",
            border_color="#4a1515", border_width=1,
            text_color="#cc5555",
            command=self._delete,
        ).pack(side="left")

        r.columnconfigure(1, weight=1)

    # ──────────────────────── DIRTY STATE ─────────────────────────

    def _snapshot(self) -> dict:
        return {
            "name":    self._name_var.get(),
            "monitor": self._monitor_var.get(),
            "gamma":   round(self._gamma_slider.get(), 2),
            "dvc":     int(self._dvc_slider.get()),
            "hue":     int(self._hue_slider.get()),
            "hotkey":  self._hotkey_var.get(),
        }

    def _mark_dirty(self):
        dirty = self._snapshot() != self._saved_values
        state = "normal" if dirty else "disabled"
        if hasattr(self, "_save_btn"):
            self._save_btn.configure(state=state)

    def _mark_clean(self):
        self._saved_values = self._snapshot()
        if hasattr(self, "_save_btn"):
            self._save_btn.configure(state="disabled")

    # ─────────────────── HOTKEY CAPTURE ──────────────────────────

    def _clear_hotkey(self):
        self._hotkey_var.set("")
        self._mark_dirty()

    def _open_hotkey_modal(self):
        import keyboard as kb

        modal = ctk.CTkToplevel(self)
        modal.overrideredirect(True)
        modal.configure(fg_color="#0f0f1a")
        modal.attributes("-topmost", True)
        modal.resizable(False, False)

        # center over parent
        self.update_idletasks()
        px, py = self.winfo_x(), self.winfo_y()
        pw, ph = self.winfo_width(), self.winfo_height()
        mw, mh = 300, 160
        modal.geometry(f"{mw}x{mh}+{px + (pw - mw)//2}+{py + (ph - mh)//2}")

        ctk.CTkLabel(
            modal, text="Asignar hotkey",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#4fa8ff",
        ).pack(pady=(20, 4))

        ctk.CTkLabel(
            modal, text="Presioná la combinación de teclas",
            font=ctk.CTkFont(size=11), text_color="#666",
        ).pack()

        combo_var = ctk.StringVar(value="...")
        ctk.CTkLabel(
            modal, textvariable=combo_var,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#ffffff",
        ).pack(pady=12)

        ctk.CTkLabel(
            modal, text="ESC para cancelar",
            font=ctk.CTkFont(size=10), text_color="#333",
        ).pack()

        keys = []
        hook = [None]

        def on_key(event):
            if event.event_type != kb.KEY_DOWN:
                return
            name = event.name
            if name == "esc":
                kb.unhook(hook[0])
                modal.destroy()
                return
            if name not in keys:
                keys.append(name)
            combo_var.set("+".join(keys))
            modifiers = {"ctrl", "alt", "shift", "windows", "left windows", "right windows"}
            if name not in modifiers and any(k in modifiers for k in keys):
                kb.unhook(hook[0])
                result = "+".join(keys)
                self._hotkey_var.set(result)
                self._mark_dirty()
                modal.destroy()

        hook[0] = kb.hook(on_key)
        modal.protocol("WM_DELETE_WINDOW", lambda: (kb.unhook(hook[0]), modal.destroy()))

    # ─────────────────── SLIDER REAL-TIME ─────────────────────────

    def _on_gamma(self, val):
        self._gamma_lbl.configure(text=f"{val:.2f}")
        self._mark_dirty()
        if hasattr(self, "_gamma_after"):
            self.after_cancel(self._gamma_after)
        self._gamma_after = self.after(120, lambda: engine.apply_gamma(round(val, 2), self._get_monitor()))

    def _on_dvc(self, val):
        self._dvc_lbl.configure(text=str(int(val)))
        engine.apply_dvc(int(val), self._get_monitor())
        self._mark_dirty()

    def _on_hue(self, val):
        self._hue_lbl.configure(text=f"{int(val)}°")
        engine.apply_hue(int(val), self._get_monitor())
        self._mark_dirty()

    def _get_monitor(self) -> int:
        val = self._monitor_var.get()
        if val == "All displays":
            return 0
        try:
            return int(val.split()[-1])
        except Exception:
            return 1

    # ─────────────────────── SELECTION ────────────────────────────

    def _select(self, name: str):
        self._selected = name
        for p in prof.get_profiles(self.config_data):
            if p["name"] == name:
                self._load_into_editor(p)
                break
        self._refresh_list()

    def _load_into_editor(self, p: dict):
        # Temporarily unbind trace to avoid spurious dirty triggers
        self._name_var.set(p["name"])
        mon = p.get("monitor", 1)
        self._monitor_var.set("All displays" if mon == 0 else f"Display {mon}")
        g = p.get("gamma", 1.0)
        self._gamma_slider.set(g)
        self._gamma_lbl.configure(text=f"{g:.2f}")
        dvc = p.get("dvc", 0)
        self._dvc_slider.set(dvc)
        self._dvc_lbl.configure(text=str(dvc))
        hue = p.get("hue", 0)
        self._hue_slider.set(hue)
        self._hue_lbl.configure(text=f"{hue}°")
        self._hotkey_var.set(p.get("hotkey", ""))
        self.after(50, self._mark_clean)   # slight delay so traces settle

    # ──────────────────────── CRUD ────────────────────────────────

    def _get_editor_values(self) -> dict:
        name = self._name_var.get().strip() or self._selected or "Sin nombre"
        return {
            "name":    name,
            "gamma":   round(self._gamma_slider.get(), 2),
            "dvc":     int(self._dvc_slider.get()),
            "hue":     int(self._hue_slider.get()),
            "monitor": self._get_monitor(),
            "hotkey":  self._hotkey_var.get().strip(),
        }

    def _reset(self):
        self._gamma_slider.set(1.0)
        self._gamma_lbl.configure(text="1.00")
        self._dvc_slider.set(0)
        self._dvc_lbl.configure(text="0")
        self._hue_slider.set(0)
        self._hue_lbl.configure(text="0°")
        engine.reset_profile(self._get_monitor())
        self._mark_dirty()

    def _save(self):
        if not self._selected:
            return
        updated = self._get_editor_values()
        if not updated["name"]:
            messagebox.showerror("Error", "El nombre no puede estar vacío", parent=self)
            return
        prof.update_profile(self.config_data, self._selected, updated)
        prof.save(self.config_data)
        self._selected = updated["name"]
        self._mark_clean()
        self._refresh_list()
        self.on_update()

    def _delete(self):
        if not self._selected:
            return
        if len(prof.get_profiles(self.config_data)) <= 1:
            messagebox.showerror("Error", "Debe haber al menos un perfil", parent=self)
            return
        prof.remove_profile(self.config_data, self._selected)
        prof.save(self.config_data)
        self._selected = None
        remaining = prof.get_profiles(self.config_data)
        if remaining:
            self._select(remaining[0]["name"])
        self.on_update()

    def _add_profile(self):
        names = {p["name"] for p in prof.get_profiles(self.config_data)}
        name, i = "Nuevo perfil", 1
        while name in names:
            name = f"Nuevo perfil {i}"; i += 1
        new = {"name": name, "gamma": 1.0, "dvc": 0, "hue": 0, "monitor": 0, "hotkey": ""}
        prof.add_profile(self.config_data, new)
        prof.save(self.config_data)
        self._select(name)

    # ─────────────────────── WINDOW ───────────────────────────────

    def refresh(self):
        self._refresh_list()

    def _position_near_tray(self):
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        w = self.winfo_reqwidth()
        h = self.winfo_reqheight()
        self.geometry(f"+{sw - w - 20}+{sh - h - 60}")

    def toggle(self):
        if self.winfo_viewable():
            self.withdraw()
        else:
            self._position_near_tray()
            self.deiconify()
            self.lift()
            self.focus_force()
