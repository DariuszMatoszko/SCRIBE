from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, simpledialog
from typing import Callable

from scribe_web.ui.controller import Controller

BUTTON_FONT = ("Helvetica", 16, "bold")
STATUS_FONT = ("Helvetica", 8, "bold")
DRAG_BAR_HEIGHT = 10
BUTTON_SIZE = 44

PANEL_BG = "#2b2b2b"
BTN_BG = "#6a6a6a"
BTN_FG = "#d9d9d9"
BTN_PRESSED_BG = PANEL_BG


def render_status(status: dict) -> str:
    session_name = status["project_name"] or "—"
    steps = status["steps"]
    pause_text = "ON" if status["paused"] else "OFF"
    last_action = status.get("last_action") or "—"
    return (
        "SESJA: {session}   KROKI: {steps}   PAUZA: {pause}   AKCJA: {action}".format(
            session=session_name,
            steps=steps,
            pause=pause_text,
            action=last_action,
        )
    )


class Panel:
    def __init__(self, controller: Controller) -> None:
        self.controller = controller
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.5)
        self.root.configure(bg=PANEL_BG)
        self.root.bind("<Escape>", lambda event: self.root.destroy())

        self._drag_offset_x = 0
        self._drag_offset_y = 0

        self._build_ui()
        self._set_session_active(False)

    def _build_ui(self) -> None:
        container = tk.Frame(self.root, bg=PANEL_BG, bd=1, relief="solid")
        container.pack(fill="both", expand=True)

        drag_bar = tk.Frame(container, bg=PANEL_BG, height=DRAG_BAR_HEIGHT, cursor="fleur")
        drag_bar.pack(fill="x")
        drag_bar.bind("<ButtonPress-1>", self._start_drag)
        drag_bar.bind("<B1-Motion>", self._on_drag)

        self.status_label = tk.Label(
            drag_bar,
            text="",
            font=STATUS_FONT,
            fg="white",
            bg=PANEL_BG,
            padx=4,
            anchor="center",
        )
        self.status_label.pack(fill="x", expand=True)
        self.status_label.bind("<ButtonPress-1>", self._start_drag)
        self.status_label.bind("<B1-Motion>", self._on_drag)

        grid = tk.Frame(container, bg=PANEL_BG, padx=4, pady=4)
        grid.pack()

        for row in range(2):
            grid.grid_rowconfigure(row, minsize=BUTTON_SIZE)
        for col in range(4):
            grid.grid_columnconfigure(col, minsize=BUTTON_SIZE)

        self.button_start = self._make_button(
            grid,
            text="S",
            command=self._on_start,
        )
        self.button_step = self._make_button(
            grid,
            text="K",
            command=self._on_step,
        )
        self.button_edit = self._make_button(
            grid,
            text="E",
            command=self._on_edit,
        )
        self.button_voice = self._make_button(
            grid,
            text="G",
            command=self._on_voice,
        )
        self.button_probe = self._make_button(
            grid,
            text="P",
            command=self._on_probe,
        )
        self.button_pause = self._make_button(
            grid,
            text="||",
            command=self._on_pause,
        )
        self.button_undo = self._make_button(
            grid,
            text="↩",
            command=self._on_undo,
        )
        self.button_end = self._make_button(
            grid,
            text="Z",
            command=self._on_end,
        )

        buttons = [
            self.button_start,
            self.button_step,
            self.button_edit,
            self.button_voice,
            self.button_probe,
            self.button_pause,
            self.button_undo,
            self.button_end,
        ]
        for index, button in enumerate(buttons):
            row = index // 4
            col = index % 4
            button.grid(row=row, column=col, padx=2, pady=2, sticky="nsew")
            self.apply_btn_normal(button)

        self._update_status_label()

    def _make_button(
        self,
        parent: tk.Widget,
        *,
        text: str,
        command: Callable[[], None],
    ) -> tk.Button:
        return tk.Button(
            parent,
            text=text,
            font=BUTTON_FONT,
            width=3,
            height=2,
            bg=BTN_BG,
            fg=BTN_FG,
            activebackground=BTN_BG,
            activeforeground=BTN_FG,
            relief="raised",
            command=command,
            borderwidth=1,
            highlightthickness=0,
        )

    def _set_session_active(self, active: bool) -> None:
        state_active = tk.NORMAL if active else tk.DISABLED
        self.button_step.configure(state=state_active)
        self.button_pause.configure(state=state_active)
        self.button_undo.configure(state=state_active)
        self.button_end.configure(state=state_active)
        self.button_start.configure(state=tk.DISABLED if active else tk.NORMAL)
        self._update_status_label()

    def _update_status_label(self) -> None:
        status = self.controller.get_status()
        self.status_label.configure(text=render_status(status))

    def apply_btn_normal(self, button: tk.Button) -> None:
        button.configure(
            bg=BTN_BG,
            fg=BTN_FG,
            relief="raised",
            activebackground=BTN_BG,
            activeforeground=BTN_FG,
        )

    def apply_btn_pressed(self, button: tk.Button) -> None:
        button.configure(
            bg=BTN_PRESSED_BG,
            fg=BTN_FG,
            relief="sunken",
            activebackground=BTN_PRESSED_BG,
            activeforeground=BTN_FG,
        )

    def flash_button(self, button: tk.Button) -> None:
        self.apply_btn_pressed(button)
        self.root.bell()
        self.root.after(
            120,
            lambda: self.apply_btn_normal(button),
        )

    def _start_drag(self, event: tk.Event) -> None:
        self._drag_offset_x = event.x_root - self.root.winfo_x()
        self._drag_offset_y = event.y_root - self.root.winfo_y()

    def _on_drag(self, event: tk.Event) -> None:
        x = event.x_root - self._drag_offset_x
        y = event.y_root - self._drag_offset_y
        self.root.geometry(f"+{x}+{y}")

    def _on_start(self) -> None:
        project_name = simpledialog.askstring("SCRIBE", "Nazwa projektu:")
        project_name = project_name.strip() if project_name else ""
        project_name = project_name or "nowa_sesja"
        self.controller.start_session(project_name)
        self._set_session_active(True)
        self.flash_button(self.button_start)
        self.apply_btn_pressed(self.button_start)
        self.button_start.config(state="disabled")
        self._update_status_label()

    def _on_step(self) -> None:
        self.controller.add_step_stub()
        self.flash_button(self.button_step)
        self._update_status_label()

    def _on_edit(self) -> None:
        self.controller.last_action = "E"
        self._update_status_label()
        messagebox.showinfo("SCRIBE", "STUB: edycja screena w Etap 4")
        self.flash_button(self.button_edit)
        self._update_status_label()

    def _on_voice(self) -> None:
        self.controller.last_action = "G"
        self._update_status_label()
        messagebox.showinfo("SCRIBE", "STUB: audio+transkrypcja w Etap 5")
        self.flash_button(self.button_voice)
        self._update_status_label()

    def _on_probe(self) -> None:
        self.controller.last_action = "P"
        self._update_status_label()
        messagebox.showinfo("SCRIBE", "STUB: probe WWW w Etap 6")
        self.flash_button(self.button_probe)
        self._update_status_label()

    def _on_pause(self) -> None:
        self.flash_button(self.button_pause)
        paused = self.controller.toggle_pause()
        if paused:
            self.root.after(130, lambda: self.apply_btn_pressed(self.button_pause))
        else:
            self.root.after(130, lambda: self.apply_btn_normal(self.button_pause))
        self._update_status_label()

    def _on_undo(self) -> None:
        self.controller.undo_last_step()
        self.flash_button(self.button_undo)
        self._update_status_label()

    def _on_end(self) -> None:
        session_dir = self.controller.end_session()
        if session_dir is not None:
            messagebox.showinfo("SCRIBE", f"Sesja zakończona: {session_dir}")
        self.flash_button(self.button_end)
        self._set_session_active(False)
        self.root.destroy()

    def run(self) -> None:
        self.root.mainloop()


def run_panel(config: dict) -> None:
    controller = Controller(config)
    panel = Panel(controller)
    panel.run()
