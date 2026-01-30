import tkinter as tk
from tkinter import messagebox, simpledialog

from .controller import Controller


PANEL_BG = "#2b2b2b"
BTN_BG = "#6a6a6a"
BTN_FG = "#d9d9d9"
BTN_BORDER = "#1f1f1f"
BTN_PRESSED_BG = PANEL_BG  # „pusty/przezroczysty” efekt

ALPHA = 0.5
FLASH_MS = 120


class CanvasButton(tk.Frame):
    """
    Własny przycisk oparty o Canvas:
    - pełna kontrola wyglądu (bez macOS-owych „humorów” tk.Button)
    - tryb momentary (flash) oraz toggle (stały stan pressed)
    """
    def __init__(self, master, text, command=None, toggle=False, width=58, height=58):
        super().__init__(master, bg=PANEL_BG, highlightthickness=0, bd=0)
        self.command = command
        self.toggle = toggle
        self.is_pressed = False
        self.enabled = True

        self.w = width
        self.h = height

        self.c = tk.Canvas(
            self,
            width=self.w,
            height=self.h,
            bg=PANEL_BG,
            highlightthickness=0,
            bd=0
        )
        self.c.pack()

        # prostokąt + tekst
        pad = 4
        self.rect = self.c.create_rectangle(
            pad, pad, self.w - pad, self.h - pad,
            fill=BTN_BG, outline=BTN_BORDER, width=2
        )
        self.txt = self.c.create_text(
            self.w / 2, self.h / 2,
            text=text,
            fill=BTN_FG,
            font=("Helvetica", 18, "bold")
        )

        # eventy
        self.c.bind("<Button-1>", self._on_click)
        self.c.bind("<Enter>", self._on_enter)
        self.c.bind("<Leave>", self._on_leave)

    def set_enabled(self, enabled: bool):
        self.enabled = enabled
        # wygląd disabled: zostaw normalny, ale przyciemnij tekst
        if not enabled:
            self.c.itemconfig(self.txt, fill="#9a9a9a")
        else:
            self.c.itemconfig(self.txt, fill=BTN_FG)

    def set_pressed(self, pressed: bool):
        self.is_pressed = pressed
        if pressed:
            self.c.itemconfig(self.rect, fill=BTN_PRESSED_BG)
        else:
            self.c.itemconfig(self.rect, fill=BTN_BG)

    def flash(self):
        # krótki flash „pusty”, potem wraca (jeśli toggle OFF)
        self.set_pressed(True)
        self.after(FLASH_MS, lambda: self.set_pressed(self.is_pressed if self.toggle else False))

    def _on_enter(self, _e):
        # delikatny outline na hover (bez zmiany tła)
        self.c.itemconfig(self.rect, outline="#3a3a3a")

    def _on_leave(self, _e):
        self.c.itemconfig(self.rect, outline=BTN_BORDER)

    def _on_click(self, _e):
        if not self.enabled:
            return

        # zawsze flash, żeby było „pstryk”
        self.flash()
        self.winfo_toplevel().bell()

        if self.toggle:
            # toggle: zmień stan na stałe
            self.set_pressed(not self.is_pressed)

        if self.command:
            self.command()


class PanelApp:
    def __init__(self, root: tk.Tk, controller: Controller):
        self.root = root
        self.controller = controller

        self.drag_off_x = 0
        self.drag_off_y = 0

        self.root.configure(bg=PANEL_BG)
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)

        # UWAGA: alpha ustawiamy na końcu initu (stabilniej na macOS)
        # self.root.attributes("-alpha", ALPHA)

        # Pasek górny do przeciągania + status
        self.top = tk.Frame(self.root, bg=PANEL_BG, height=22)
        self.top.grid(row=0, column=0, sticky="ew")
        self.top.grid_columnconfigure(0, weight=1)

        self.status_var = tk.StringVar(value=self._render_status())
        self.status_lbl = tk.Label(
            self.top,
            textvariable=self.status_var,
            bg=PANEL_BG,
            fg="#cfcfcf",
            font=("Helvetica", 11, "bold"),
            anchor="center",
            padx=8
        )
        self.status_lbl.grid(row=0, column=0, sticky="ew")

        # Drag
        for w in (self.top, self.status_lbl):
            w.bind("<ButtonPress-1>", self._start_move)
            w.bind("<B1-Motion>", self._on_move)

        # Siatka przycisków
        self.grid = tk.Frame(self.root, bg=PANEL_BG)
        self.grid.grid(row=1, column=0, padx=6, pady=6)

        # Rząd 1: S K E G
        self.btnS = CanvasButton(self.grid, "S", command=self.on_start, toggle=True)
        self.btnK = CanvasButton(self.grid, "K", command=self.on_step, toggle=False)
        self.btnE = CanvasButton(self.grid, "E", command=self.on_edit, toggle=False)
        self.btnG = CanvasButton(self.grid, "G", command=self.on_voice, toggle=False)

        # Rząd 2: P || ↩ Z
        self.btnP = CanvasButton(self.grid, "P", command=self.on_probe, toggle=False)
        self.btnPause = CanvasButton(self.grid, "||", command=self.on_pause, toggle=True)
        self.btnUndo = CanvasButton(self.grid, "↩", command=self.on_undo, toggle=False)
        self.btnZ = CanvasButton(self.grid, "Z", command=self.on_end, toggle=False)

        self._place_buttons()

        # skrót awaryjny
        self.root.bind("<Escape>", lambda _e: self.root.destroy())

        # na starcie tylko S ma sens
        self._set_controls_started(False)

        # alpha na końcu
        self.root.attributes("-alpha", ALPHA)

    def _place_buttons(self):
        # 2x4
        self.btnS.grid(row=0, column=0, padx=4, pady=4)
        self.btnK.grid(row=0, column=1, padx=4, pady=4)
        self.btnE.grid(row=0, column=2, padx=4, pady=4)
        self.btnG.grid(row=0, column=3, padx=4, pady=4)

        self.btnP.grid(row=1, column=0, padx=4, pady=4)
        self.btnPause.grid(row=1, column=1, padx=4, pady=4)
        self.btnUndo.grid(row=1, column=2, padx=4, pady=4)
        self.btnZ.grid(row=1, column=3, padx=4, pady=4)

    def _set_controls_started(self, started: bool):
        # S: enabled zawsze, ale po starcie blokujemy (żeby nie robić 2 sesji)
        if started:
            self.btnS.set_enabled(False)  # S zostaje „wciśnięte” i zablokowane
            self.btnS.set_pressed(True)
        else:
            self.btnS.set_enabled(True)
            self.btnS.set_pressed(False)

        # reszta aktywna dopiero po starcie
        for b in (self.btnK, self.btnE, self.btnG, self.btnP, self.btnPause, self.btnUndo, self.btnZ):
            b.set_enabled(started)
            if b is self.btnPause:
                b.set_pressed(False)  # pauza OFF na start

    def _render_status(self) -> str:
        st = self.controller.get_status()
        name = st.get("project_name") or "—"
        steps = st.get("steps", 0)
        paused = "ON" if st.get("paused") else "OFF"
        action = st.get("last_action") or "—"
        return f"SESJA: {name}   KROKI: {steps}   PAUZA: {paused}   AKCJA: {action}"

    def _refresh_status(self):
        self.status_var.set(self._render_status())

    def _start_move(self, event):
        self.drag_off_x = event.x
        self.drag_off_y = event.y

    def _on_move(self, event):
        x = self.root.winfo_x() + (event.x - self.drag_off_x)
        y = self.root.winfo_y() + (event.y - self.drag_off_y)
        self.root.geometry(f"+{x}+{y}")

    # Handlery
    def on_start(self):
        name = simpledialog.askstring("SCRIBE", "Nazwa projektu:", parent=self.root)
        if name is None:
            # cancel -> nic
            self.btnS.set_pressed(False)
            return
        name = name.strip()
        if not name:
            name = "nowa_sesja"

        self.controller.start_session(name)
        self._set_controls_started(True)
        self._refresh_status()

    def on_step(self):
        self.controller.add_step_stub()
        self._refresh_status()

    def on_edit(self):
        # STUB – etap 4
        self.controller.last_action = "E"
        self._refresh_status()
        messagebox.showinfo("SCRIBE", "STUB: edycja screena w Etap 4")

    def on_voice(self):
        # STUB – etap 5
        self.controller.last_action = "G"
        self._refresh_status()
        messagebox.showinfo("SCRIBE", "STUB: audio+transkrypcja w Etap 5")

    def on_probe(self):
        # STUB – etap 6
        self.controller.last_action = "P"
        self._refresh_status()
        messagebox.showinfo("SCRIBE", "STUB: probe WWW w Etap 6")

    def on_pause(self):
        paused = self.controller.toggle_pause()
        # ustaw stan toggle zgodnie z kontrolerem
        self.btnPause.set_pressed(paused)
        self._refresh_status()

    def on_undo(self):
        self.controller.undo_last_step()
        self._refresh_status()

    def on_end(self):
        sd = self.controller.end_session()
        if sd:
            messagebox.showinfo("SCRIBE", f"Zapisano sesję:\n{sd}")
        self.root.destroy()


def run_panel(config: dict):
    root = tk.Tk()
    root.title("SCRIBE")
    ctrl = Controller(config)
    app = PanelApp(root, ctrl)

    # sensowna pozycja startowa
    root.geometry("+200+200")
    root.mainloop()
