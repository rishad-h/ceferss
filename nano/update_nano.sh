#!/bin/bash

# This script automates updating the Arduino Nano and restarting the Pi's service.

# --- Configuration ---
SKETCH_PATH="nano_grid" # The sketch is in a directory named "nano_grid"
FQBN="arduino:avr:nano:cpu=atmega328old" # Arduino Nano with Old Bootloader
PORT="/dev/ttyUSB0"      # Hardcoded port for the Arduino Nano

echo "--> Stopping sensor service..."
sudo systemctl stop sensor.service

# Wait for the service to fully stop and release the port
echo "--> Waiting for service to stop and port to be released..."
for i in {1..10}; do
    if ! sudo lsof "$PORT" > /dev/null 2>&1; then
        echo "--> Port $PORT is now free (attempt $i)"
        break
    fi
    echo "--> Port still in use, waiting... (attempt $i/10)"
    sleep 1
done

# Final check if port is still in use
if sudo lsof "$PORT" > /dev/null 2>&1; then
    echo "ERROR: Port $PORT is still in use after 10 seconds. Force killing processes..."
    sudo pkill -f "soft_sense_nano.py"
    sleep 2
fi

echo "--> Using hardcoded port: $PORT"

echo "--> Compiling and uploading sketch ($SKETCH_PATH) to Nano..."
# Navigate to the script's directory to find the sketch file
cd "$(dirname "$0")" || exit

# First compile the sketch
echo "--> Compiling sketch..."
arduino-cli compile --fqbn "$FQBN" "$SKETCH_PATH"

# Check if compilation was successful
if [ $? -ne 0 ]; then
    echo "Error: Compilation failed. The sensor service will be restarted, but the Nano was not updated."
    sudo systemctl restart sensor.service
    exit 1
fi

# Then upload the compiled sketch
echo "--> Uploading to device..."
arduino-cli upload -p "$PORT" --fqbn "$FQBN" "$SKETCH_PATH"

# Check if the upload was successful
if [ $? -ne 0 ]; then
    echo "Error: Upload failed. The sensor service will be restarted, but the Nano was not updated."
    sudo systemctl restart sensor.service
    exit 1
fi

echo "--> Waiting for Nano to reboot (3 seconds)..."
sleep 3

echo "--> Restarting sensor service..."
sudo systemctl restart sensor.service

echo "--> Update complete. Verifying service status:"
# Wait a final moment for the service to initialize before checking status
sleep 1
sudo systemctl status sensor.service
