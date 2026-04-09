#!/usr/bin/env python3
"""
GUI for visualizing a row/column conductive-strip sensor grid.

Adjust:
  - number of rows
  - number of columns
  - strip width  (in) — same for rows and columns
  - strip gap    (in) — same for rows and columns

Reports:
  - Resolution: smallest discernable distance (pitch = width + gap)
  - Usable space: fraction of the bounding sensor area covered by
    row/column intersections (where touch is actually sensed).
"""

import os
import tkinter as tk
from tkinter import ttk

PRESETS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "designs_info.txt")


def load_presets(path=PRESETS_FILE):
    """Parse designs_info.txt into a list of (name, dict) presets.

    Format: blank-line-separated blocks; first non-empty line is the
    preset name, remaining lines are 'key: value' pairs.
    """
    presets = []
    if not os.path.exists(path):
        return presets
    with open(path) as f:
        blocks = f.read().split("\n\n")
    for block in blocks:
        lines = [ln.strip() for ln in block.splitlines() if ln.strip()]
        if not lines:
            continue
        name = lines[0]
        data = {}
        for ln in lines[1:]:
            if ":" not in ln:
                continue
            k, v = ln.split(":", 1)
            try:
                data[k.strip()] = float(v.strip())
            except ValueError:
                pass
        try:
            presets.append((name, {
                "rows": int(data["rows"]),
                "cols": int(data["cols"]),
                "width": data["strip width (in)"],
                "gap": data["strip gap (in)"],
            }))
        except KeyError:
            continue
    return presets


class SensorGUI:
    def __init__(self, root):
        self.root = root
        root.title("CEFERSS Sensor Visualizer")

        self.rows = tk.IntVar(value=9)
        self.cols = tk.IntVar(value=9)
        self.width = tk.DoubleVar(value=0.20)  # in
        self.gap = tk.DoubleVar(value=0.08)    # in

        main = ttk.Frame(root, padding=10)
        main.grid(row=0, column=0, sticky="nsew")

        # Left: canvas
        self.canvas = tk.Canvas(main, width=500, height=500,
                                bg="white", highlightthickness=1,
                                highlightbackground="#888")
        self.canvas.grid(row=0, column=0, rowspan=3, padx=(0, 10),
                         sticky="nsew")
        self.canvas.bind("<Configure>", lambda e: self.redraw())

        # Right: sliders
        controls = ttk.LabelFrame(main, text="Parameters", padding=10)
        controls.grid(row=0, column=1, sticky="new")

        # Right: results (created before sliders so initial redraw works)
        results = ttk.LabelFrame(main, text="Results", padding=10)
        results.grid(row=1, column=1, sticky="new", pady=(10, 0))

        self.res_label = ttk.Label(results, text="", font=("TkDefaultFont", 11))
        self.res_label.pack(anchor="w")
        self.usable_label = ttk.Label(results, text="",
                                      font=("TkDefaultFont", 11))
        self.usable_label.pack(anchor="w", pady=(4, 0))
        self.size_label = ttk.Label(results, text="",
                                    font=("TkDefaultFont", 11))
        self.size_label.pack(anchor="w", pady=(4, 0))

        self._add_slider(controls, "Rows", self.rows, 1, 50, 0, is_int=True)
        self._add_slider(controls, "Columns", self.cols, 1, 50, 1, is_int=True)
        self._add_slider(controls, "Strip width (in)", self.width,
                         0.1, 2.0, 2)
        self._add_slider(controls, "Strip gap (in)", self.gap,
                         0.04, 1.5, 3)

        # Presets (loaded from designs_info.txt)
        presets = ttk.LabelFrame(main, text="Presets", padding=10)
        presets.grid(row=2, column=1, sticky="new", pady=(10, 0))
        for name, cfg in load_presets():
            ttk.Button(
                presets, text=name,
                command=lambda c=cfg: self._load_preset(
                    c["rows"], c["cols"], c["width"], c["gap"])
            ).pack(fill="x", pady=2)

        main.columnconfigure(0, weight=1)
        main.rowconfigure(0, weight=1)
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        self.redraw()

    def _load_preset(self, rows, cols, width, gap):
        self.rows.set(rows)
        self.cols.set(cols)
        self.width.set(width)
        self.gap.set(gap)
        self.redraw()

    def _add_slider(self, parent, label, var, lo, hi, row, is_int=False):
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w")
        val_lbl = ttk.Label(parent, width=6, anchor="e")
        val_lbl.grid(row=row, column=2, padx=(6, 0))

        def on_change(_=None):
            if is_int:
                var.set(int(float(var.get())))
                val_lbl.config(text=f"{var.get()}")
            else:
                val_lbl.config(text=f"{var.get():.2f}")
            self.redraw()

        scale = ttk.Scale(parent, from_=lo, to=hi, variable=var,
                          orient="horizontal", length=220, command=on_change)
        scale.grid(row=row, column=1, padx=6, pady=4)
        var.trace_add("write", lambda *_: on_change())
        on_change()

    def redraw(self):
        c = self.canvas
        c.delete("all")
        try:
            n_r = max(1, int(self.rows.get()))
            n_c = max(1, int(self.cols.get()))
            w = max(0.01, float(self.width.get()))
            g = max(0.0, float(self.gap.get()))
        except tk.TclError:
            return

        # Physical dimensions (in)
        total_h = n_r * w + (n_r - 1) * g
        total_w = n_c * w + (n_c - 1) * g

        # Resolution = pitch (center-to-center of adjacent strips)
        pitch = w + g

        # Usable space: fraction of bounding area covered by strip
        # intersections (the cells where both a row and a column strip
        # overlap — where touches are actually localized).
        intersect_area = (n_r * w) * (n_c * w)
        total_area = total_h * total_w
        usable_frac = intersect_area / total_area if total_area > 0 else 0.0

        self.res_label.config(text=f"Resolution (pitch): {pitch:.2f} in")
        self.usable_label.config(
            text=f"Usable space: {usable_frac * 100:.1f}%")
        self.size_label.config(
            text=f"Sensor size: {total_w:.1f} × {total_h:.1f} in")

        # Draw to canvas
        cw = c.winfo_width() or 500
        ch = c.winfo_height() or 500
        pad = 36
        avail_w = cw - 2 * pad
        avail_h = ch - 2 * pad
        if total_w <= 0 or total_h <= 0:
            return
        scale = min(avail_w / total_w, avail_h / total_h)
        draw_w = total_w * scale
        draw_h = total_h * scale
        x0 = (cw - draw_w) / 2
        y0 = (ch - draw_h) / 2

        # Bounding box
        c.create_rectangle(x0, y0, x0 + draw_w, y0 + draw_h,
                           outline="#bbb", dash=(2, 2))

        # Inch rulers (top, bottom, left, right)
        major = 8  # major tick length
        minor = 4  # minor tick length
        # Horizontal ticks
        i = 0
        while i * scale <= draw_w + 1e-6:
            x = x0 + i * scale
            c.create_line(x, y0, x, y0 - major, fill="#444")
            c.create_line(x, y0 + draw_h, x, y0 + draw_h + major,
                          fill="#444")
            c.create_text(x, y0 - major - 2, text=f"{i}\"",
                          anchor="s", fill="#444",
                          font=("TkDefaultFont", 8))
            c.create_text(x, y0 + draw_h + major + 2, text=f"{i}\"",
                          anchor="n", fill="#444",
                          font=("TkDefaultFont", 8))
            # quarter-inch minor ticks
            for q in (0.25, 0.5, 0.75):
                xm = x + q * scale
                if xm <= x0 + draw_w + 1e-6:
                    c.create_line(xm, y0, xm, y0 - minor, fill="#888")
                    c.create_line(xm, y0 + draw_h, xm,
                                  y0 + draw_h + minor, fill="#888")
            i += 1
        # Vertical ticks
        j = 0
        while j * scale <= draw_h + 1e-6:
            y = y0 + j * scale
            c.create_line(x0, y, x0 - major, y, fill="#444")
            c.create_line(x0 + draw_w, y, x0 + draw_w + major, y,
                          fill="#444")
            c.create_text(x0 - major - 2, y, text=f"{j}\"",
                          anchor="e", fill="#444",
                          font=("TkDefaultFont", 8))
            c.create_text(x0 + draw_w + major + 2, y, text=f"{j}\"",
                          anchor="w", fill="#444",
                          font=("TkDefaultFont", 8))
            for q in (0.25, 0.5, 0.75):
                ym = y + q * scale
                if ym <= y0 + draw_h + 1e-6:
                    c.create_line(x0, ym, x0 - minor, ym, fill="#888")
                    c.create_line(x0 + draw_w, ym,
                                  x0 + draw_w + minor, ym, fill="#888")
            j += 1

        # Column strips (vertical) — blue
        for i in range(n_c):
            x = x0 + i * (w + g) * scale
            c.create_rectangle(x, y0, x + w * scale, y0 + draw_h,
                               fill="#4a90e2", outline="")

        # Row strips (horizontal) — red, semi via stipple
        for j in range(n_r):
            y = y0 + j * (w + g) * scale
            c.create_rectangle(x0, y, x0 + draw_w, y + w * scale,
                               fill="#e24a4a", outline="", stipple="gray50")

        # Highlight intersections
        for i in range(n_c):
            for j in range(n_r):
                x = x0 + i * (w + g) * scale
                y = y0 + j * (w + g) * scale
                c.create_rectangle(x, y, x + w * scale, y + w * scale,
                                   fill="#7a2bbf", outline="")


def main():
    root = tk.Tk()
    SensorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
