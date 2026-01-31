import tkinter as tk
from tkinter import messagebox

from .controller import Controller


PANEL_BG = "#2b2b2b"
BTN_BG = "#6a6a6a"
BTN_FG = "#d9d9d9"
BTN_PRESSED_BG = PANEL_BG

ALPHA = 0.5
FLASH_MS = 120


class CanvasButton(tk.Frame):
    def __init__(
        self,
        master,
        text,
        command=None,
        toggle=False,
        width=40,
        height=40,
    ):
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
            bd=0,
        )
        self.c.pack()

        pad = 2
        self.rect = self.c.create_rectangle(
            pad,
            pad,
            self.w - pad,
            self.h - pad,
            fill=BTN_BG,
            outline="",
            width=0,
        )
        self.txt = self.c.create_text(
            self.w / 2,
            self.h / 2,
            text=text,
            fill=BTN_FG,
            font=("Helvetica", 16, "bold"),
        )

        self.c.bind("<Button-1>", self._on_click)

    def set_enabled(self, enabled: bool):
        self.enabled = enabled
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
        self.set_pressed(True)
        self.after(FLASH_MS, lambda: self.set_pressed(self.is_pressed if self.toggle else False))

    def _on_click(self, _e):
        if not self.enabled:
            return
        self.winfo_toplevel().bell()
        self.flash()
        if self.toggle:
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

        self.top = tk.Frame(self.root, bg=PANEL_BG, height=18)
        self.top.grid(row=0, column=0, sticky="ew")
        self.top.grid_columnconfigure(0, weight=1)

        self.status_var_line1 = tk.StringVar()
        self.status_var_line2 = tk.StringVar()
        self.status_lbl_line1 = tk.Label(
            self.top,
            textvariable=self.status_var_line1,
            bg=PANEL_BG,
            fg="#cfcfcf",
            font=("Helvetica", 9, "bold"),
            anchor="center",
            padx=1,
            pady=0,
            justify="center",
        )
        self.status_lbl_line1.grid(row=0, column=0, sticky="ew")

        self.status_lbl_line2 = tk.Label(
            self.top,
            textvariable=self.status_var_line2,
            bg=PANEL_BG,
            fg="#cfcfcf",
            font=("Helvetica", 9, "bold"),
            anchor="center",
            padx=1,
            pady=0,
            justify="center",
        )
        self.status_lbl_line2.grid(row=1, column=0, sticky="ew")

        for w in (self.top, self.status_lbl_line1, self.status_lbl_line2):
            w.bind("<ButtonPress-1>", self._start_move)
            w.bind("<B1-Motion>", self._on_move)

        self.grid = tk.Frame(self.root, bg=PANEL_BG)
        self.grid.grid(row=1, column=0, padx=0, pady=0)

        self.btnS = CanvasButton(self.grid, "S", command=self.on_start, toggle=True)
        self.btnK = CanvasButton(self.grid, "K", command=self.on_step)
        self.btnE = CanvasButton(self.grid, "E", command=self.on_edit)
        self.btnG = CanvasButton(self.grid, "G", command=self.on_voice)

        self.btnP = CanvasButton(self.grid, "P", command=self.on_probe)
        self.btnPause = CanvasButton(self.grid, "||", command=self.on_pause, toggle=True)
        self.btnUndo = CanvasButton(self.grid, "↩", command=self.on_undo)
        self.btnZ = CanvasButton(self.grid, "Z", command=self.on_end)

        self._place_buttons()

        self.root.bind("<Escape>", lambda _e: self.root.destroy())

        self._set_controls_started(False)

        self.root.attributes("-alpha", ALPHA)
        self._refresh_status()

    def _place_buttons(self):
        self.btnS.grid(row=0, column=0, padx=1, pady=1)
        self.btnK.grid(row=0, column=1, padx=1, pady=1)
        self.btnE.grid(row=0, column=2, padx=1, pady=1)
        self.btnG.grid(row=0, column=3, padx=1, pady=1)

        self.btnP.grid(row=1, column=0, padx=1, pady=1)
        self.btnPause.grid(row=1, column=1, padx=1, pady=1)
        self.btnUndo.grid(row=1, column=2, padx=1, pady=1)
        self.btnZ.grid(row=1, column=3, padx=1, pady=1)

    def _ask_project_name(self) -> str | None:
        dialog = tk.Toplevel(self.root)
        dialog.overrideredirect(True)
        dialog.configure(bg=PANEL_BG)
        dialog.attributes("-topmost", True)

        result = {"value": None}

        entry = tk.Entry(
            dialog,
            bg="#3a3a3a",
            fg=BTN_FG,
            insertbackground=BTN_FG,
            relief="flat",
            highlightthickness=0,
        )
        entry.pack(fill=tk.X, padx=2, pady=2)

        def on_ok(_event=None):
            result["value"] = entry.get().strip()
            dialog.destroy()

        def on_cancel(_event=None):
            result["value"] = None
            dialog.destroy()

        for target in (dialog, entry):
            target.bind("<Return>", on_ok)
            target.bind("<Escape>", on_cancel)
        dialog.protocol("WM_DELETE_WINDOW", on_cancel)

        dialog.update_idletasks()
        self.root.update_idletasks()
        panel_w = self.root.winfo_width()
        height = entry.winfo_reqheight() + 4
        x = self.root.winfo_x()
        y = self.root.winfo_y() - height - 12
        if y < 10:
            y = self.root.winfo_y() + self.root.winfo_height() + 12
        dialog.geometry(f"{panel_w}x{height}+{x}+{y}")

        entry.focus_force()
        dialog.grab_set()
        dialog.wait_window()
        return result["value"]

    def _set_controls_started(self, started: bool):
        if started:
            self.btnS.set_enabled(False)
            self.btnS.set_pressed(True)
        else:
            self.btnS.set_enabled(True)
            self.btnS.set_pressed(False)

        for b in (self.btnK, self.btnE, self.btnG, self.btnP, self.btnPause, self.btnUndo, self.btnZ):
            b.set_enabled(started)
            if b is self.btnPause:
                b.set_pressed(False)

    def _render_status_lines(self) -> tuple[str, str]:
        st = self.controller.get_status()
        name = st.get("project_name") or "—"
        steps = st.get("steps", 0)
        paused = "ON" if st.get("paused") else "OFF"
        action = st.get("last_action") or "—"
        line1 = f"SESJA: {name}   KROKI: {steps}"
        line2 = f"PAUZA: {paused}   AKCJA: {action}"
        return line1, line2

    def _refresh_status(self):
        line1, line2 = self._render_status_lines()
        self.status_var_line1.set(line1)
        self.status_var_line2.set(line2)
        self.root.update_idletasks()
        wrap_w = self.grid.winfo_width()
        if wrap_w:
            for lbl in (self.status_lbl_line1, self.status_lbl_line2):
                lbl.configure(wraplength=wrap_w)

    def _start_move(self, event):
        self.drag_off_x = event.x
        self.drag_off_y = event.y

    def _on_move(self, event):
        x = self.root.winfo_x() + (event.x - self.drag_off_x)
        y = self.root.winfo_y() + (event.y - self.drag_off_y)
        self.root.geometry(f"+{x}+{y}")

    def on_start(self):
        name = self._ask_project_name()
        if name is None:
            self.btnS.set_pressed(False)
            return
        name = name.strip()
        if not name:
            name = "nowa_sesja"

        self.controller.start_session(name)
        self._set_controls_started(True)
        self._refresh_status()

    def on_step(self):
        self.controller.add_step_screenshot()
        self._refresh_status()

    def on_edit(self):
        ok = self.controller.annotate_last_step()
        self._refresh_status()
        if not ok:
            messagebox.showinfo("SCRIBE", "Najpierw zrób K")

    def on_voice(self):
        self.controller.last_action = "G"
        self._refresh_status()
        self.root.after(10, self._show_voice_stub)

    def _show_voice_stub(self):
        messagebox.showinfo("SCRIBE", "STUB: audio+transkrypcja w Etap 5")

    def on_probe(self):
        self.controller.last_action = "P"
        self._refresh_status()
        self.root.after(10, self._show_probe_stub)

    def _show_probe_stub(self):
        messagebox.showinfo("SCRIBE", "STUB: probe WWW w Etap 6")

    def on_pause(self):
        paused = self.controller.toggle_pause()
        self.btnPause.set_pressed(paused)
        self._refresh_status()

    def on_undo(self):
        self.controller.undo_last_step()
        self._refresh_status()

    def on_end(self):
        self.root.after(10, self._end_after_flash)

    def _end_after_flash(self):
        sd = self.controller.end_session()
        if sd:
            messagebox.showinfo("SCRIBE", f"Zapisano sesję:\n{sd}")
        self.root.destroy()


def run_panel(config: dict):
    root = tk.Tk()
    root.title("SCRIBE")
    ctrl = Controller(config)
    PanelApp(root, ctrl)

    root.geometry("+200+200")
    root.mainloop()
