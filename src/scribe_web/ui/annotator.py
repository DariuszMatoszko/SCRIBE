from __future__ import annotations

from pathlib import Path
import tkinter as tk

from PIL import Image, ImageDraw, ImageTk


MAX_WIDTH = 1100
MAX_HEIGHT = 800
STROKE_COLOR = "red"
STROKE_WIDTH = 6


def _scale_to_fit(width: int, height: int) -> tuple[int, int, float]:
    scale = min(MAX_WIDTH / width, MAX_HEIGHT / height, 1.0)
    return int(width * scale), int(height * scale), scale


def annotate_freehand(input_png: Path, output_png: Path) -> bool:
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

    segments: list[tuple[int, int, int, int]] = []
    last_point = {"x": None, "y": None}
    saved = {"ok": False}

    def on_press(event):
        last_point["x"] = event.x
        last_point["y"] = event.y

    def on_drag(event):
        if last_point["x"] is None or last_point["y"] is None:
            return
        x1 = last_point["x"]
        y1 = last_point["y"]
        x2 = event.x
        y2 = event.y
        segments.append((x1, y1, x2, y2))
        canvas.create_line(
            x1,
            y1,
            x2,
            y2,
            fill=STROKE_COLOR,
            width=STROKE_WIDTH,
            capstyle=tk.ROUND,
            smooth=True,
        )
        last_point["x"] = x2
        last_point["y"] = y2

    def on_release(_event):
        last_point["x"] = None
        last_point["y"] = None

    def on_save(_event=None):
        if not segments:
            saved["ok"] = False
            root.destroy()
            return
        annotated = image.copy()
        draw = ImageDraw.Draw(annotated)
        for x1, y1, x2, y2 in segments:
            draw.line(
                [x1 / scale, y1 / scale, x2 / scale, y2 / scale],
                fill=STROKE_COLOR,
                width=STROKE_WIDTH,
                joint="round",
            )
        output_png.parent.mkdir(parents=True, exist_ok=True)
        annotated.save(output_png, format="PNG")
        saved["ok"] = True
        root.destroy()

    def on_cancel(_event=None):
        saved["ok"] = False
        root.destroy()

    canvas.bind("<ButtonPress-1>", on_press)
    canvas.bind("<B1-Motion>", on_drag)
    canvas.bind("<ButtonRelease-1>", on_release)

    root.bind("<Return>", on_save)
    root.bind("<Escape>", on_cancel)
    root.protocol("WM_DELETE_WINDOW", on_cancel)
    root.mainloop()
    return saved["ok"]
