# ============================================================
#  Simple Matrix Scanner — MicroPython for RP2350 Pico 2
#
#  Wiring:
#    Row pins:    GPIO 0-8  (outputs — driven LOW one at a time)
#    Column pins: GPIO 9-17 (inputs  — pulled UP, read for LOWs)
#
#  Active-low scanning:
#    - All row pins idle HIGH
#    - One row pulled LOW at a time
#    - Contact pulls column input LOW  →  detected as '0'
#    - PULL_UP on columns prevents floating-pin false positives
#
#  Output format (plain UART / USB serial, 115200 baud):
#    One CSV line per scan: 81 comma-separated values, '0'=contact '1'=open
#    Example: 1,1,0,1,1,1,1,1,1,1,0,1,...\n
#
#  Run matrix_visualizer.py on your PC to display this data.
# ============================================================
from machine import Pin, UART
import sys
import time

# --- Pin Configuration ---
NUM_ROWS = 9
NUM_COLS = 9
ROW_PIN_BASE = 0   # GPIOs 0-8  (outputs)
COL_PIN_BASE = 9   # GPIOs 9-17 (inputs)

SETTLE_MS  = 5     # settle time after driving row LOW
SCAN_MS    = 20    # delay between scans (~20 Hz)

# --- Setup pins ---
row_pins = []
for r in range(NUM_ROWS):
    p = Pin(ROW_PIN_BASE + r, Pin.OUT)
    p.on()   # idle HIGH
    row_pins.append(p)

col_pins = []
for c in range(NUM_COLS):
    p = Pin(COL_PIN_BASE + c, Pin.IN, Pin.PULL_UP)
    col_pins.append(p)

# --- Scan ---
def scan():
    grid = [[False] * NUM_COLS for _ in range(NUM_ROWS)]
    for r in range(NUM_ROWS):
        row_pins[r].off()
        time.sleep_ms(SETTLE_MS)
        for c in range(NUM_COLS):
            grid[r][c] = col_pins[c].value() == 0   # LOW = contact
        row_pins[r].on()
        time.sleep_ms(1)
    return grid

# --- Output ---
# Emit a single CSV line so the PC visualizer can parse it directly.
def emit(grid):
    values = []
    for r in range(NUM_ROWS):
        for c in range(NUM_COLS):
            values.append('0' if grid[r][c] else '1')
    sys.stdout.write(','.join(values) + '\n')

# --- Main loop ---
while True:
    emit(scan())
    time.sleep_ms(SCAN_MS)
