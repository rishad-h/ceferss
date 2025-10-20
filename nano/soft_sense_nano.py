import serial
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import sh1106
import time

# --- SYSTEM CONFIG ---
SERIAL_PORT = '/dev/ttyUSB0'
BAUD_RATE = 115200

# --- GRID CONFIG ---
CELL_SIZE = 10
CELL_GAP = 2
GRID_COLS = 5
GRID_ROWS = 5 # Display a 5x5 grid

GRID_WIDTH = (CELL_SIZE * GRID_COLS) + (CELL_GAP * (GRID_COLS - 1))
GRID_HEIGHT = (CELL_SIZE * GRID_ROWS) + (CELL_GAP * (GRID_ROWS - 1))

def draw_grid(device, grid_states, offset_x, offset_y):
    """Draw the entire grid based on the current states."""
    with canvas(device) as draw:
        for r in range(GRID_ROWS):
            for c in range(GRID_COLS):
                index = r * GRID_COLS + c
                
                x1 = offset_x + (c * (CELL_SIZE + CELL_GAP))
                y1 = offset_y + (r * (CELL_SIZE + CELL_GAP))
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE
                
                # print(grid_states[index])
                # '0' means touch (LOW), so we fill the square
                # Pico sends 0 for touch, 1 for no touch
                if index < len(grid_states) and grid_states[index] == '0':
                    draw.rectangle((x1, y1, x2, y2), outline="white", fill="white")
                else:
                    draw.rectangle((x1, y1, x2, y2), outline="white", fill="black")

def main():
    try:
        i2c_bus = i2c(port=1, address=0x3C)
        device = sh1106(i2c_bus, rotate=0)
        device.clear()
        
        OFFSET_X = (device.width - GRID_WIDTH) // 2
        OFFSET_Y = (device.height - GRID_HEIGHT) // 2

        print(f"Connecting to Arduino Nano on {SERIAL_PORT}...")
        # --- OPTIMIZATION: Reduce timeout to prevent long hangs ---
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
        ser.flush()
        print("Connection successful. Reading 5x5 grid from Nano...")

        # Initialize with an empty grid state
        grid_states = ['1'] * (GRID_ROWS * GRID_COLS)
        
        # --- OPTIMIZATION: Draw the initial empty grid once ---
        draw_grid(device, grid_states, OFFSET_X, OFFSET_Y)
        
        while True:
         # Check if there's data waiting in the serial buffer
         if ser.in_waiting > 0:
             try:
                 line = ser.readline().decode('utf-8').strip()
                 print(f"Received: {line}")  # Debug output
                 
                 # Ensure the line is not empty and has the correct format
                 if line and line.count(',') == (GRID_ROWS * GRID_COLS - 1):
                     new_states = line.split(',')
                     
                     # --- OPTIMIZATION: Only redraw if the state has changed ---
                     if new_states != grid_states:
                         grid_states = new_states
                         draw_grid(device, grid_states, OFFSET_X, OFFSET_Y)
                         print(f"Updated grid: {grid_states}")
                 else:
                     print(f"Invalid data format: {line}")
                     
             except UnicodeDecodeError:
                 # Handle cases where incomplete data is read
                 print("Warning: UnicodeDecodeError. Flushing input.")
                 ser.flushInput()
            
        # Sleep briefly to yield CPU time. 20Hz = 50ms.
        # We can sleep for less to ensure high responsiveness.
        time.sleep(0.02) # Loop at ~50Hz

    except serial.SerialException as e:
        print(f"Error: Could not open serial port {SERIAL_PORT}. {e}")
    except FileNotFoundError:
        print(f"Error: Serial port {SERIAL_PORT} not found.")
    except KeyboardInterrupt:
        print("\nProgram stopped.")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
        if 'device' in locals():
            device.clear()

if __name__ == "__main__":
    main()
