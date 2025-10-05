import serial
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import sh1106
from PIL import ImageDraw
import time

# --- SYSTEM CONFIG ---
# Bus 002 Device 002: ID 1a86:7523 QinHeng Electronics CH340 serial converter
SERIAL_PORT = '/dev/ttyUSB0' # change depending on port
BAUD_RATE = 115200

# --- GRID CONFIG ---
CELL_SIZE = 10  # 10x10 pixel squares
CELL_GAP = 2    # 2-pixel gap
GRID_COLS = 5
GRID_ROWS = 5

# calculate total grid size
GRID_WIDTH = (CELL_SIZE * GRID_COLS) + (CELL_GAP * (GRID_COLS - 1))
GRID_HEIGHT = (CELL_SIZE * GRID_ROWS) + (CELL_GAP * (GRID_ROWS - 1))

def main():
    try:
        i2c_bus = i2c(port=1, address=0x3C) # change depending on setup
        device = sh1106(i2c_bus, rotate=0)
        device.clear()
        
        OFFSET_X = (device.width - GRID_WIDTH) // 2
        OFFSET_Y = (device.height - GRID_HEIGHT) // 2

        print(f"Connecting to Arduino on {SERIAL_PORT}...")
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        ser.flush()
        print("Connection successful. Reading 5x5 grid...")

        while True:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8').rstrip()

                # --- UPDATED CHECK FOR 25 VALUES ---
                # (25 values = 24 commas)
                if line and line.count(',') == 24:
                    grid_states = line.split(',')

                    with canvas(device) as draw:
                        for r in range(GRID_ROWS):
                            for c in range(GRID_COLS):
                                index = r * GRID_COLS + c
                                
                                x1 = OFFSET_X + (c * (CELL_SIZE + CELL_GAP))
                                y1 = OFFSET_Y + (r * (CELL_SIZE + CELL_GAP))
                                x2 = x1 + CELL_SIZE
                                y2 = y1 + CELL_SIZE
                                
                                if grid_states[index] == '0':
                                    draw.rectangle((x1, y1, x2, y2), outline="white", fill="white")
                                else:
                                    draw.rectangle((x1, y1, x2, y2), outline="white", fill="black")
                
            time.sleep(0.01)

    except serial.SerialException as e:
        print(f"Error: Could not open serial port {SERIAL_PORT}.")
        print("Please check the port name and permissions.")
    except FileNotFoundError:
        print(f"Error: Serial port {SERIAL_PORT} not found.")
        print("Is the Arduino plugged in?")
    except KeyboardInterrupt:
        print("\nProgram stopped.")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
        if 'device' in locals():
            device.clear()

if __name__ == "__main__":
    main()