#!/usr/bin/env python3
"""
Terminal visualizer for Raspberry Pi Pico 9x9 sensor grid.
Reads grid state directly from serial (USB) and displays it in the terminal.

Usage: python3 pico_visualizer.py [serial_port]
  Default port: auto-detected (Pico shows up as /dev/tty.usbmodem* on macOS
  or /dev/ttyACM* on Linux)
"""

import sys
import glob
import serial
import serial.tools.list_ports

# --- Configuration ---
BAUD_RATE = 115200
GRID_ROWS = 9
GRID_COLS = 9
CELL_W = 6   # characters wide per cell (must be even)
CELL_H = 2   # lines tall per cell


def find_serial_port():
    """Auto-detect the Pico serial port."""
    # Prefer ports whose description/hwid look like a Pico
    for p in serial.tools.list_ports.comports():
        desc = (p.description or "").lower()
        hwid = (p.hwid or "").lower()
        if any(k in desc or k in hwid for k in ("pico", "rp2", "2e8a", "micropython")):
            return p.device

    # Fall back to common device patterns
    patterns = [
        "/dev/tty.usbmodem*",
        "/dev/ttyACM*",
        "/dev/tty.usbserial-*",
        "/dev/ttyUSB*",
    ]
    for pattern in patterns:
        ports = glob.glob(pattern)
        if ports:
            return ports[0]
    return None


def clear_screen():
    """Move cursor to top-left to overwrite previous frame."""
    print("\033[H\033[J", end="")


def render(grid_states):
    """Render a large grid and active cell count side by side."""
    active = sum(1 for s in grid_states if s == "0")
    total = GRID_ROWS * GRID_COLS

    clear_screen()

    gap = "        "

    # build grid lines
    top_border = "┌" + ("─" * CELL_W + "┬") * (GRID_COLS - 1) + "─" * CELL_W + "┐"
    mid_border = "├" + ("─" * CELL_W + "┼") * (GRID_COLS - 1) + "─" * CELL_W + "┤"
    bot_border = "└" + ("─" * CELL_W + "┴") * (GRID_COLS - 1) + "─" * CELL_W + "┘"

    touch_fill = "█" * CELL_W
    empty_fill = "░" * CELL_W

    # pre-build all grid output lines
    lines = []
    lines.append(f"  {GRID_ROWS}x{GRID_COLS} Sensor Grid")
    lines.append("  " + top_border)

    for r in range(GRID_ROWS):
        for _ in range(CELL_H):
            row_str = "  │"
            for c in range(GRID_COLS):
                index = r * GRID_COLS + c
                if index < len(grid_states) and grid_states[index] == "0":
                    row_str += touch_fill
                else:
                    row_str += empty_fill
                row_str += "│"
            lines.append(row_str)
        if r < GRID_ROWS - 1:
            lines.append("  " + mid_border)

    lines.append("  " + bot_border)
    lines.append("")
    lines.append("  ██ = touch    ░░ = no touch")
    lines.append("  Press Ctrl+C to quit")

    # build side panel content (vertically centered next to the grid)
    panel_lines = [
        "┌─────────────────────┐",
        "│       Status        │",
        "│                     │",
        f"│  Active: {active:>3} / {total:<3} │",
        "│                     │",
    ]
    bar_len = int((active / total) * 16)
    bar = "█" * bar_len + "░" * (16 - bar_len)
    panel_lines.append(f"│ [{bar}]  │")
    panel_lines.append("│                     │")
    panel_lines.append("└─────────────────────┘")

    # figure out where to place the panel (vertically centered)
    panel_start = max(1, (len(lines) - len(panel_lines)) // 2)

    # print with side panel merged in
    for i, line in enumerate(lines):
        pi = i - panel_start
        if 0 <= pi < len(panel_lines):
            print(line + gap + panel_lines[pi])
        else:
            print(line)


def main():
    # determine serial port
    if len(sys.argv) > 1:
        port = sys.argv[1]
    else:
        port = find_serial_port()
        if port is None:
            print("Error: No Pico serial port found.")
            print("Usage: python3 pico_visualizer.py [serial_port]")
            print("Example: python3 pico_visualizer.py /dev/tty.usbmodem1101")
            sys.exit(1)

    print(f"Connecting to {port} at {BAUD_RATE} baud...")

    try:
        ser = serial.Serial(port, BAUD_RATE, timeout=1)
        print("Connected! Waiting for data...")

        while True:
            line = ser.readline().decode("utf-8", errors="ignore").strip()
            if not line:
                continue

            parts = line.split(",")
            if len(parts) == GRID_ROWS * GRID_COLS:
                render(parts)

    except serial.SerialException as e:
        print(f"Serial error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nStopping visualizer...")
    finally:
        if "ser" in locals():
            ser.close()


if __name__ == "__main__":
    main()
