#!/usr/bin/env python3
"""
Sensor designer.

Given a target sensor length, width, and minimum discernable distance
(in inches), compute and visualize the strip layout. Strip-to-strip gap
is fixed at 0.25 in. The minimum discernable distance is taken to be
the strip width itself — two touches separated by less than one strip
width may land on the same strip and become indistinguishable. With
gap fixed, setting strip_width = min_distance maximizes the usable
sensing area for the given resolution requirement:

    strip_width = min_distance
    pitch       = strip_width + gap
    n_strips    = floor((dimension + gap) / pitch)
"""

import math
import tkinter as tk
from tkinter import ttk

GAP = 0.25  # inches, fixed


def design(length, width, min_distance, gap=GAP):
    if min_distance <= 0:
        raise ValueError("Minimum discernable distance must be > 0.")
    strip_w = min_distance
    pitch = strip_w + gap
    n_rows = max(1, math.floor((length + gap) / pitch))
    n_cols = max(1, math.floor((width + gap) / pitch))
    actual_l = n_rows * strip_w + (n_rows - 1) * gap
    actual_w = n_cols * strip_w + (n_cols - 1) * gap
    return {
        "strip_width": strip_w, "gap": gap,
        "rows": n_rows, "cols": n_cols,
        "actual_length": actual_l, "actual_width": actual_w,
    }


class DesignerGUI:
    def __init__(self, root):
        self.root = root
        root.title("CEFERSS Sensor Designer")

        self.length = tk.StringVar(value="12.0")
        self.width = tk.StringVar(value="12.0")
        self.dist = tk.StringVar(value="0.5")

        main = ttk.Frame(root, padding=10)
        main.grid(row=0, column=0, sticky="nsew")

        # Left: canvas
        self.canvas = tk.Canvas(main, width=500, height=500,
                                bg="white", highlightthickness=1,
                                highlightbackground="#888")
        self.canvas.grid(row=0, column=0, rowspan=2, padx=(0, 10),
                         sticky="nsew")
        self.canvas.bind("<Configure>", lambda e: self.redraw())

        # Right: inputs
        controls = ttk.LabelFrame(main, text="Target", padding=10)
        controls.grid(row=0, column=1, sticky="new")
        self._row(controls, "Sensor length (in)", self.length, 0)
        self._row(controls, "Sensor width (in)", self.width, 1)
        self._row(controls, "Min discernable distance (in)", self.dist, 2)
        ttk.Label(controls, text=f"Fixed gap: {GAP} in",
                  foreground="#666").grid(row=3, column=0, columnspan=2,
                                          sticky="w", pady=(6, 0))

        # Right: results
        results = ttk.LabelFrame(main, text="Results", padding=10)
        results.grid(row=1, column=1, sticky="new", pady=(10, 0))
        self.strip_label = ttk.Label(results, text="",
                                     font=("TkDefaultFont", 11))
        self.strip_label.pack(anchor="w")
        self.gap_label = ttk.Label(results, text="",
                                   font=("TkDefaultFont", 11))
        self.gap_label.pack(anchor="w", pady=(4, 0))
        self.count_label = ttk.Label(results, text="",
                                     font=("TkDefaultFont", 11))
        self.count_label.pack(anchor="w", pady=(4, 0))
        self.size_label = ttk.Label(results, text="",
                                    font=("TkDefaultFont", 11))
        self.size_label.pack(anchor="w", pady=(4, 0))
        self.usable_label = ttk.Label(results, text="",
                                      font=("TkDefaultFont", 11))
        self.usable_label.pack(anchor="w", pady=(4, 0))
        self.err_label = ttk.Label(results, text="", foreground="#c00",
                                   font=("TkDefaultFont", 10))
        self.err_label.pack(anchor="w")

        for v in (self.length, self.width, self.dist):
            v.trace_add("write", lambda *_: self.redraw())

        main.columnconfigure(0, weight=1)
        main.rowconfigure(0, weight=1)
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        self.redraw()

    def _row(self, parent, label, var, row):
        ttk.Label(parent, text=label).grid(row=row, column=0,
                                           sticky="w", pady=2)
        ttk.Entry(parent, textvariable=var, width=12).grid(
            row=row, column=1, sticky="ew", padx=(8, 0))

    def redraw(self):
        c = self.canvas
        c.delete("all")
        self.err_label.config(text="")
        try:
            L = float(self.length.get())
            W = float(self.width.get())
            md = float(self.dist.get())
            d = design(L, W, md)
        except (ValueError, ZeroDivisionError) as exc:
            self.err_label.config(text=str(exc))
            self.strip_label.config(text="")
            self.gap_label.config(text="")
            self.count_label.config(text="")
            self.size_label.config(text="")
            self.usable_label.config(text="")
            return

        n_r = d["rows"]
        n_c = d["cols"]
        w = d["strip_width"]
        g = d["gap"]
        total_h = d["actual_length"]
        total_w = d["actual_width"]

        self.strip_label.config(text=f"Strip width: {w:.3f} in")
        self.gap_label.config(text=f"Strip gap: {g:.3f} in")
        self.count_label.config(text=f"Rows: {n_r}   Cols: {n_c}")
        self.size_label.config(
            text=f"Actual: {total_w:.2f} × {total_h:.2f} in")
        intersect_area = (n_r * w) * (n_c * w)
        total_area = total_h * total_w
        usable_frac = intersect_area / total_area if total_area > 0 else 0.0
        self.usable_label.config(
            text=f"Usable area: {usable_frac * 100:.1f}%")

        cw = c.winfo_width() or 500
        ch = c.winfo_height() or 500
        pad = 36
        avail_w = cw - 2 * pad
        avail_h = ch - 2 * pad
        if total_w <= 0 or total_h <= 0 or avail_w <= 0 or avail_h <= 0:
            return
        scale = min(avail_w / total_w, avail_h / total_h)
        draw_w = total_w * scale
        draw_h = total_h * scale
        x0 = (cw - draw_w) / 2
        y0 = (ch - draw_h) / 2

        # Bounding box
        c.create_rectangle(x0, y0, x0 + draw_w, y0 + draw_h,
                           outline="#bbb", dash=(2, 2))

        # Inch rulers
        major = 8
        minor = 4
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
            for q in (0.25, 0.5, 0.75):
                xm = x + q * scale
                if xm <= x0 + draw_w + 1e-6:
                    c.create_line(xm, y0, xm, y0 - minor, fill="#888")
                    c.create_line(xm, y0 + draw_h, xm,
                                  y0 + draw_h + minor, fill="#888")
            i += 1
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

        # Columns (blue)
        for i in range(n_c):
            x = x0 + i * (w + g) * scale
            c.create_rectangle(x, y0, x + w * scale, y0 + draw_h,
                               fill="#4a90e2", outline="")
        # Rows (red stippled)
        for j in range(n_r):
            y = y0 + j * (w + g) * scale
            c.create_rectangle(x0, y, x0 + draw_w, y + w * scale,
                               fill="#e24a4a", outline="",
                               stipple="gray50")
        # Intersections
        for i in range(n_c):
            for j in range(n_r):
                x = x0 + i * (w + g) * scale
                y = y0 + j * (w + g) * scale
                c.create_rectangle(x, y, x + w * scale, y + w * scale,
                                   fill="#7a2bbf", outline="")


def main():
    root = tk.Tk()
    DesignerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
