from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, simpledialog
from typing import Callable

from scribe_web.ui.controller import Controller

BUTTON_FONT = ("Helvetica", 16, "bold")
STATUS_FONT = ("Helvetica", 8, "bold")
DRAG_BAR_HEIGHT = 10
BUTTON_SIZE = 44

COLOR_BG = "#1b1b1b"
COLOR_DRAG = "#2c2c2c"
COLOR_GRAY = "#5f6368"
COLOR_GREEN = "#2ecc71"
COLOR_RED = "#e74c3c"
COLOR_AMBER = "#f0ad4e"
COLOR_AMBER_ACTIVE = "#ffe08a"


class Panel:
    def __init__(self, controller: Controller) -> None:
        self.controller = controller
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.5)
        self.root.configure(bg=COLOR_BG)
        self.root.bind("<Escape>", lambda event: self.root.destroy())

        self._drag_offset_x = 0
        self._drag_offset_y = 0

        self._build_ui()
        self._set_session_active(False)

    def _build_ui(self) -> None:
        container = tk.Frame(self.root, bg=COLOR_BG, bd=1, relief="solid")
        container.pack(fill="both", expand=True)

        drag_bar = tk.Frame(container, bg=COLOR_DRAG, height=DRAG_BAR_HEIGHT, cursor="fleur")
        drag_bar.pack(fill="x")
        drag_bar.bind("<ButtonPress-1>", self._start_drag)
        drag_bar.bind("<B1-Motion>", self._on_drag)

        self.status_label = tk.Label(
            drag_bar,
            text="",
            font=STATUS_FONT,
            fg="white",
            bg=COLOR_DRAG,
            padx=4,
        )
        self.status_label.pack(side="left")
        self.status_label.bind("<ButtonPress-1>", self._start_drag)
        self.status_label.bind("<B1-Motion>", self._on_drag)

        grid = tk.Frame(container, bg=COLOR_BG, padx=4, pady=4)
        grid.pack()

        for row in range(2):
            grid.grid_rowconfigure(row, minsize=BUTTON_SIZE)
        for col in range(4):
            grid.grid_columnconfigure(col, minsize=BUTTON_SIZE)

        self.button_start = self._make_button(
            grid,
            text="S",
            color=COLOR_GREEN,
            command=self._on_start,
        )
        self.button_step = self._make_button(
            grid,
            text="K",
            color=COLOR_GRAY,
            command=self._on_step,
        )
        self.button_edit = self._make_button(
            grid,
            text="E",
            color=COLOR_GRAY,
            command=self._on_edit,
        )
        self.button_voice = self._make_button(
            grid,
            text="G",
            color=COLOR_GRAY,
            command=self._on_voice,
        )
        self.button_probe = self._make_button(
            grid,
            text="P",
            color=COLOR_GRAY,
            command=self._on_probe,
        )
        self.button_pause = self._make_button(
            grid,
            text="||",
            color=COLOR_AMBER,
            command=self._on_pause,
            fg="black",
        )
        self.button_undo = self._make_button(
            grid,
            text="↩",
            color=COLOR_GRAY,
            command=self._on_undo,
        )
        self.button_end = self._make_button(
            grid,
            text="Z",
            color=COLOR_RED,
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

        self._update_status_label()

    def _make_button(
        self,
        parent: tk.Widget,
        *,
        text: str,
        color: str,
        command: Callable[[], None],
        fg: str = "white",
    ) -> tk.Button:
        return tk.Button(
            parent,
            text=text,
            font=BUTTON_FONT,
            width=3,
            height=2,
            bg=color,
            fg=fg,
            activebackground=color,
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
        project_name = status["project_name"] or "-"
        pause_text = "ON" if status["paused"] else "OFF"
        status_text = f"SESJA: {project_name}  KROKI: {status['steps']}  PAUZA: {pause_text}"
        self.status_label.configure(text=status_text)

    def _update_pause_style(self, paused: bool) -> None:
        if paused:
            self.button_pause.configure(
                relief="sunken",
                bg=COLOR_AMBER_ACTIVE,
                activebackground=COLOR_AMBER_ACTIVE,
            )
        else:
            self.button_pause.configure(
                relief="raised",
                bg=COLOR_AMBER,
                activebackground=COLOR_AMBER,
            )

    def _flash_button(self, button: tk.Button, *, restore_relief: str = "raised") -> None:
        button.configure(relief="sunken")
        self.root.bell()
        self.root.after(120, lambda: button.configure(relief=restore_relief))

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
        self._update_pause_style(False)
        self._set_session_active(True)
        self._flash_button(self.button_start)
        self._update_status_label()

    def _on_step(self) -> None:
        self.controller.add_step_stub()
        self._flash_button(self.button_step)
        self._update_status_label()

    def _on_edit(self) -> None:
        messagebox.showinfo("SCRIBE", "STUB: edycja screena w Etap 4")
        self._flash_button(self.button_edit)
        self._update_status_label()

    def _on_voice(self) -> None:
        messagebox.showinfo("SCRIBE", "STUB: audio+transkrypcja w Etap 5")
        self._flash_button(self.button_voice)
        self._update_status_label()

    def _on_probe(self) -> None:
        messagebox.showinfo("SCRIBE", "STUB: probe WWW w Etap 6")
        self._flash_button(self.button_probe)
        self._update_status_label()

    def _on_pause(self) -> None:
        paused = self.controller.toggle_pause()
        restore_relief = "sunken" if paused else "raised"
        self._flash_button(self.button_pause, restore_relief=restore_relief)
        self._update_pause_style(paused)
        self._update_status_label()

    def _on_undo(self) -> None:
        self.controller.undo_last_step()
        self._flash_button(self.button_undo)
        self._update_status_label()

    def _on_end(self) -> None:
        session_dir = self.controller.end_session()
        if session_dir is not None:
            messagebox.showinfo("SCRIBE", f"Sesja zakończona: {session_dir}")
        self._flash_button(self.button_end)
        self._set_session_active(False)
        self.root.destroy()

    def run(self) -> None:
        self.root.mainloop()


def run_panel(config: dict) -> None:
    controller = Controller(config)
    panel = Panel(controller)
    panel.run()
