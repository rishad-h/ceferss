#!/usr/bin/env python3
"""
Remote visualizer for Arduino Nano grid data.
This script connects to the serial forwarder on the Pi 5 and visualizes the grid.
Run this on your remote device after SSH port forwarding.
"""

import socket
import sys

# --- Configuration ---
TCP_HOST = 'localhost'  # After SSH port forwarding
TCP_PORT = 5555
GRID_ROWS = 5
GRID_COLS = 5

def visualize_grid(grid_states):
    """Simple ASCII visualization of the grid."""
    print("\n" + "="*30)
    for r in range(GRID_ROWS):
        row_str = ""
        for c in range(GRID_COLS):
            index = r * GRID_COLS + c
            if index < len(grid_states):
                # '0' = touch (show as █), '1' = no touch (show as ░)
                row_str += "█ " if grid_states[index] == '0' else "░ "
            else:
                row_str += "? "
        print(row_str)
    print("="*30)

def main():
    """Connect to the serial forwarder and visualize data."""
    try:
        print(f"Connecting to serial forwarder at {TCP_HOST}:{TCP_PORT}...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((TCP_HOST, TCP_PORT))
        print("Connected! Receiving data...")
        
        buffer = b""
        
        while True:
            # Receive data
            data = sock.recv(1024)
            if not data:
                print("Connection closed by server")
                break
            
            buffer += data
            
            # Process complete lines
            while b'\n' in buffer:
                line, buffer = buffer.split(b'\n', 1)
                line_str = line.decode('utf-8').strip()
                
                # Validate and visualize
                if line_str and line_str.count(',') == (GRID_ROWS * GRID_COLS - 1):
                    grid_states = line_str.split(',')
                    visualize_grid(grid_states)
                    print(f"Raw data: {line_str}")
                else:
                    print(f"Invalid data: {line_str}")
                    
    except ConnectionRefusedError:
        print(f"Error: Could not connect to {TCP_HOST}:{TCP_PORT}")
        print("Make sure:")
        print("1. The serial forwarder is running on the Pi 5")
        print(f"2. You've set up SSH port forwarding: ssh -L {TCP_PORT}:localhost:{TCP_PORT} user@pi5")
    except KeyboardInterrupt:
        print("\nStopping visualizer...")
    finally:
        if 'sock' in locals():
            sock.close()

if __name__ == "__main__":
    main()
