#!/usr/bin/env python3
"""
Matrix grid visualizer — reads comma-separated contact data from a serial
port and renders it in-place in the terminal using ANSI escape codes.

Data format expected from the Pico:
  One line per scan, values separated by commas.
  '0' = contact (touch), '1' = no contact
  Example for a 9x9 grid:
    1,1,0,1,1,1,1,1,1,1,1,1,...  (81 values)

Usage:
  python3 matrix_visualizer.py
  python3 matrix_visualizer.py --port /dev/ttyUSB0 --baud 115200
  python3 matrix_visualizer.py --port COM3 --rows 5 --cols 5

Install dependencies:
  pip install pyserial
"""

import serial
import serial.tools.list_ports
import argparse
import sys
import time
import os

# --- Default configuration ---
DEFAULT_PORT  = None        # Auto-detected if not specified
DEFAULT_BAUD  = 115200
DEFAULT_ROWS  = 9
DEFAULT_COLS  = 9

# --- ANSI helpers ---
ESC = "\x1b["

def ansi(code):
    sys.stdout.write(ESC + code)

def clear_screen():
    sys.stdout.write("\x1b[2J\x1b[H")

def move(row, col):
    sys.stdout.write(f"\x1b[{row};{col}H")

def hide_cursor():
    sys.stdout.write("\x1b[?25l")

def show_cursor():
    sys.stdout.write("\x1b[?25h")

def bold(s):
    return f"\x1b[1m{s}\x1b[0m"

def dim(s):
    return f"\x1b[2m{s}\x1b[0m"

def green(s):
    return f"\x1b[32m{s}\x1b[0m"

def red(s):
    return f"\x1b[31m{s}\x1b[0m"

def yellow(s):
    return f"\x1b[33m{s}\x1b[0m"

def cyan(s):
    return f"\x1b[36m{s}\x1b[0m"

def write(s):
    sys.stdout.write(s)

def flush():
    sys.stdout.flush()

# --- Port auto-detection ---
def find_pico_port():
    """Try to find a connected Pico or similar USB serial device."""
    candidates = list(serial.tools.list_ports.comports())
    # Prefer known Pico VID/PID or description keywords
    for p in candidates:
        desc = (p.description or "").lower()
        hwid = (p.hwid or "").lower()
        if any(k in desc or k in hwid for k in ("pico", "rp2", "2e8a", "micropython", "cdc")):
            return p.device
    # Fall back to first available port
    if candidates:
        return candidates[0].device
    return None

def list_ports():
    ports = list(serial.tools.list_ports.comports())
    if not ports:
        print("No serial ports found.")
        return
    print("Available serial ports:")
    for p in ports:
        print(f"  {p.device:20s}  {p.description}")

# --- Draw ---
def draw(grid_states, rows, cols, scan_num, fps, raw_line, port, baud):
    total = rows * cols
    active = sum(1 for v in grid_states[:total] if v == '0')

    move(1, 1)
    write(bold("Matrix Visualizer") + "  " +
          cyan(f"{rows}x{cols}") + "  " +
          dim(f"port: {port}  baud: {baud}"))
    write("  " * 10)   # clear trailing chars

    move(2, 1)
    write(dim(f"scan #{scan_num:<7}  fps: {fps:<4}  active: {active}/{total}"))
    write("  " * 10)

    # Column header
    move(3, 1)
    write(dim("    "))
    for c in range(cols):
        write(dim(f"C{c:<2}"))
    write("\n")

    move(4, 1)
    write(dim("    " + "---" * cols))

    # Grid rows
    for r in range(rows):
        move(5 + r, 1)
        write(dim(f"R{r:<2} "))
        for c in range(cols):
            idx = r * cols + c
            if idx < len(grid_states):
                on = grid_states[idx] == '0'
                if on:
                    write(green(" █ "))
                else:
                    write(dim(" ░ "))
            else:
                write("  ?")

    # Active contacts list
    contacts_row = 5 + rows + 1
    move(contacts_row, 1)
    write(dim("-" * (4 + cols * 3)))

    contacts = [
        (r, c)
        for r in range(rows)
        for c in range(cols)
        if r * cols + c < len(grid_states) and grid_states[r * cols + c] == '0'
    ]

    move(contacts_row + 1, 1)
    if contacts:
        write(f"Active contacts ({len(contacts)}):  ")
        pairs = ", ".join(f"R{r}C{c}" for r, c in contacts[:20])
        if len(contacts) > 20:
            pairs += f" +{len(contacts)-20} more"
        write(pairs)
        write(" " * 10)
    else:
        write(dim("No contacts detected") + " " * 20)

    # Raw data line
    move(contacts_row + 3, 1)
    raw_display = raw_line[:80] + ("…" if len(raw_line) > 80 else "")
    write(dim("raw: " + raw_display) + " " * 5)

    # Park cursor
    move(contacts_row + 5, 1)
    flush()

# --- Main ---
def main():
    parser = argparse.ArgumentParser(description="Matrix grid serial visualizer")
    parser.add_argument("--port",  default=None,         help="Serial port (e.g. /dev/ttyACM0, COM3)")
    parser.add_argument("--baud",  default=DEFAULT_BAUD, type=int, help="Baud rate (default 115200)")
    parser.add_argument("--rows",  default=DEFAULT_ROWS, type=int, help="Grid rows (default 9)")
    parser.add_argument("--cols",  default=DEFAULT_COLS, type=int, help="Grid cols (default 9)")
    parser.add_argument("--list",  action="store_true",              help="List available serial ports and exit")
    args = parser.parse_args()

    if args.list:
        list_ports()
        return

    port = args.port
    if not port:
        port = find_pico_port()
        if not port:
            print(red("No serial port found. Use --port /dev/ttyACM0 or --list to see options."))
            sys.exit(1)
        print(f"Auto-detected port: {yellow(port)}")
        time.sleep(0.5)

    rows, cols = args.rows, args.cols
    expected_values = rows * cols

    print(f"Connecting to {port} at {args.baud} baud...")
    try:
        ser = serial.Serial(port, args.baud, timeout=1)
    except serial.SerialException as e:
        print(red(f"Could not open port: {e}"))
        sys.exit(1)

    time.sleep(0.1)
    ser.reset_input_buffer()

    hide_cursor()
    clear_screen()

    scan_num   = 0
    fps_count  = 0
    fps        = 0
    last_fps   = time.time()
    buf        = b""

    try:
        while True:
            chunk = ser.read(ser.in_waiting or 1)
            if chunk:
                buf += chunk

            while b'\n' in buf:
                line_bytes, buf = buf.split(b'\n', 1)
                try:
                    line = line_bytes.decode('utf-8', errors='replace').strip()
                except Exception:
                    continue

                parts = line.split(',')
                if len(parts) != expected_values:
                    # Non-data line (startup messages etc) — skip silently
                    continue

                scan_num  += 1
                fps_count += 1
                now = time.time()
                if now - last_fps >= 1.0:
                    fps       = fps_count
                    fps_count = 0
                    last_fps  = now

                draw(parts, rows, cols, scan_num, fps, line, port, args.baud)

    except KeyboardInterrupt:
        pass
    finally:
        show_cursor()
        move(100, 1)
        flush()
        ser.close()
        print("\nStopped.")

if __name__ == "__main__":
    main()