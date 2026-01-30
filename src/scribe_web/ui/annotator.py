from __future__ import annotations

from pathlib import Path
import tkinter as tk
from tkinter import messagebox

from PIL import Image, ImageDraw, ImageTk


MAX_WIDTH = 1100
MAX_HEIGHT = 800
OUTLINE_COLOR = "red"
OUTLINE_WIDTH = 4


def _scale_to_fit(width: int, height: int) -> tuple[int, int, float]:
    scale = min(MAX_WIDTH / width, MAX_HEIGHT / height, 1.0)
    return int(width * scale), int(height * scale), scale


def annotate_image(input_png: Path, output_png: Path) -> bool:
    image = Image.open(input_png).convert("RGB")
    orig_w, orig_h = image.size
    disp_w, disp_h, scale = _scale_to_fit(orig_w, orig_h)

    root = tk.Tk()
    root.title("SCRIBE: Annotate")
    root.attributes("-topmost", True)

    canvas = tk.Canvas(root, width=disp_w, height=disp_h, highlightthickness=0)
    canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=False)

    display_img = image.resize((disp_w, disp_h), Image.LANCZOS) if scale != 1.0 else image
    tk_img = ImageTk.PhotoImage(display_img)
    canvas.create_image(0, 0, anchor="nw", image=tk_img)
    canvas.image = tk_img

    rect_id = None
    start = {"x": 0, "y": 0}
    end = {"x": 0, "y": 0}
    saved = {"ok": False}

    def on_press(event):
        start["x"] = event.x
        start["y"] = event.y
        end["x"] = event.x
        end["y"] = event.y
        nonlocal rect_id
        if rect_id is not None:
            canvas.delete(rect_id)
        rect_id = canvas.create_rectangle(
            start["x"],
            start["y"],
            end["x"],
            end["y"],
            outline=OUTLINE_COLOR,
            width=OUTLINE_WIDTH,
        )

    def on_drag(event):
        end["x"] = event.x
        end["y"] = event.y
        if rect_id is not None:
            canvas.coords(rect_id, start["x"], start["y"], end["x"], end["y"])

    def on_save():
        if rect_id is None:
            messagebox.showinfo("SCRIBE", "Najpierw narysuj prostokąt.")
            return
        x1 = min(start["x"], end["x"]) / scale
        y1 = min(start["y"], end["y"]) / scale
        x2 = max(start["x"], end["x"]) / scale
        y2 = max(start["y"], end["y"]) / scale
        x1 = max(0, min(orig_w, int(x1)))
        y1 = max(0, min(orig_h, int(y1)))
        x2 = max(0, min(orig_w, int(x2)))
        y2 = max(0, min(orig_h, int(y2)))

        annotated = image.copy()
        draw = ImageDraw.Draw(annotated)
        draw.rectangle([x1, y1, x2, y2], outline=OUTLINE_COLOR, width=OUTLINE_WIDTH)

        output_png.parent.mkdir(parents=True, exist_ok=True)
        annotated.save(output_png, format="PNG")
        saved["ok"] = True
        root.destroy()

    def on_cancel():
        saved["ok"] = False
        root.destroy()

    canvas.bind("<ButtonPress-1>", on_press)
    canvas.bind("<B1-Motion>", on_drag)

    btn_frame = tk.Frame(root)
    btn_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=6)
    btn_save = tk.Button(btn_frame, text="Save", command=on_save, width=10)
    btn_cancel = tk.Button(btn_frame, text="Cancel", command=on_cancel, width=10)
    btn_save.pack(side=tk.LEFT, padx=10)
    btn_cancel.pack(side=tk.RIGHT, padx=10)

    root.protocol("WM_DELETE_WINDOW", on_cancel)
    root.mainloop()
    return saved["ok"]
