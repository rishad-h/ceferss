#!/usr/bin/env python3
"""
Serial-to-TCP forwarder for Arduino Nano grid data.
This script reads from the Arduino Nano and forwards the data to any connected TCP clients.
"""

import serial
import socket
import threading
import time

# --- Configuration ---
SERIAL_PORT = '/dev/ttyUSB0'
BAUD_RATE = 115200
TCP_HOST = '0.0.0.0'  # Listen on all network interfaces
TCP_PORT = 5555       # Port for clients to connect to

# List to store connected clients
clients = []
clients_lock = threading.Lock()

def handle_client(client_socket, client_address):
    """Handle a connected client."""
    print(f"New client connected: {client_address}")
    with clients_lock:
        clients.append(client_socket)
    
    try:
        # Keep the connection alive until the client disconnects
        while True:
            time.sleep(1)
    except Exception as e:
        print(f"Client {client_address} error: {e}")
    finally:
        with clients_lock:
            if client_socket in clients:
                clients.remove(client_socket)
        client_socket.close()
        print(f"Client disconnected: {client_address}")

def broadcast_to_clients(data):
    """Send data to all connected clients."""
    with clients_lock:
        disconnected = []
        for client in clients:
            try:
                client.sendall(data)
            except Exception as e:
                print(f"Error sending to client: {e}")
                disconnected.append(client)
        
        # Remove disconnected clients
        for client in disconnected:
            clients.remove(client)
            client.close()

def serial_reader(ser):
    """Read from serial port and broadcast to all clients."""
    print(f"Reading from {SERIAL_PORT}...")
    while True:
        try:
            if ser.in_waiting > 0:
                line = ser.readline()
                print(f"Received: {line.decode('utf-8').strip()}")
                broadcast_to_clients(line)
        except Exception as e:
            print(f"Serial read error: {e}")
            time.sleep(1)

def main():
    """Main function to start the serial forwarder."""
    try:
        # Open serial port
        print(f"Opening serial port {SERIAL_PORT}...")
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
        ser.flush()
        print(f"Serial port opened successfully")
        
        # Start serial reader thread
        serial_thread = threading.Thread(target=serial_reader, args=(ser,), daemon=True)
        serial_thread.start()
        
        # Create TCP server
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((TCP_HOST, TCP_PORT))
        server_socket.listen(5)
        
        print(f"TCP server listening on {TCP_HOST}:{TCP_PORT}")
        print(f"Clients can connect using: ssh -L {TCP_PORT}:localhost:{TCP_PORT} user@pi5-hostname")
        print("Press Ctrl+C to stop")
        
        # Accept client connections
        while True:
            client_socket, client_address = server_socket.accept()
            client_thread = threading.Thread(
                target=handle_client, 
                args=(client_socket, client_address), 
                daemon=True
            )
            client_thread.start()
            
    except serial.SerialException as e:
        print(f"Error: Could not open serial port {SERIAL_PORT}. {e}")
    except KeyboardInterrupt:
        print("\nStopping server...")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
        if 'server_socket' in locals():
            server_socket.close()

if __name__ == "__main__":
    main()
