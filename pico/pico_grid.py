# Raspberry Pi Pico H version - OPTIMIZED
# 5x5 matrix scanning with state change detection

import machine
import time

# Grid configuration
ROW_COUNT = 5
COL_COUNT = 5

# Row pins (outputs): GP3, GP4, GP5, GP6, GP2
row_pins = [machine.Pin(i, machine.Pin.OUT) for i in [3, 4, 5, 6, 2]]

# Column pins (inputs with pull-up): GP8, GP9, GP10, GP11, GP7
col_pins = [machine.Pin(i, machine.Pin.IN, machine.Pin.PULL_UP) for i in [8, 9, 10, 11, 7]]

# --- OPTIMIZATION: Store previous state to send data only on change ---
# Initialize with a state that will trigger the first send
last_grid_state = [1] * (ROW_COUNT * COL_COUNT)
current_grid_state = [1] * (ROW_COUNT * COL_COUNT)

# Initialize UART for communication with Raspberry Pi
# Use a buffer to handle data more efficiently
uart = machine.UART(0, baudrate=115200, tx=machine.Pin(0), rx=machine.Pin(1))

def setup():
    """Initialize the pins"""
    for pin in row_pins:
        pin.value(1)  # Set all rows to HIGH (inactive)
    print("Pico H 5x5 Touch Matrix Optimized and Initialized")

def scan_matrix():
    """
    Scan the 5x5 matrix and update the global current_grid_state.
    Returns True if the state has changed, False otherwise.
    """
    state_changed = False
    
    for r in range(ROW_COUNT):
        row_pins[r].value(0)  # Set current row to LOW (active)
        time.sleep_us(10)      # Small delay to let the signal settle
        
        for c in range(COL_COUNT):
            index = r * COL_COUNT + c
            # Reading is inverted: 0 = touch, 1 = no touch
            reading = col_pins[c].value()
            
            # --- OPTIMIZATION: Directly update the current state list ---
            if current_grid_state[index] != reading:
                current_grid_state[index] = reading
                state_changed = True
        
        row_pins[r].value(1)  # Reset current row to HIGH (inactive)
        
    return state_changed

def main():
    """Main loop: scan matrix and send data to Pi 5 only when it changes."""
    setup()
    
    # Send initial state to sync with Pi 5
    initial_data_string = ','.join(map(str, last_grid_state))
    uart.write(initial_data_string + '\n')
    uart.flush()
    print("Initial state sent")
    
    # Counter for periodic sends
    send_counter = 0
    
    while True:
        # Scan the matrix and check if anything has changed
        state_changed = scan_matrix()
        
        if state_changed:
            # --- OPTIMIZATION: Construct string and send only if state has changed ---
            data_string = ','.join(map(str, current_grid_state))
            
            # Send the new grid state over UART
            uart.write(data_string + '\n')
            uart.flush()  # CRITICAL: Ensure data is sent immediately
            
            # Debug: Show when data is sent
            print(f"Sent: {data_string}")
            
            # Update last state
            last_grid_state[:] = current_grid_state[:]
        
        # Send data every 50 iterations (1 second) even if no change
        send_counter += 1
        if send_counter >= 50:
            data_string = ','.join(map(str, current_grid_state))
            uart.write(data_string + '\n')
            uart.flush()
            print(f"Periodic send: {data_string}")
            send_counter = 0

        # The loop can run very fast. A small sleep prevents 100% CPU usage.
        # Target 20Hz is a 50ms loop time. We can sleep for less to be safe.
        time.sleep_ms(20) # Approx 50Hz, well above the 20Hz target

# Run the main function
if __name__ == "__main__":
    main()
