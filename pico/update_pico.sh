#!/bin/bash

# This script automates updating the Pico and restarting the Pi's service.

echo "--> Stopping sensor service..."
sudo systemctl stop sensor.service

# Wait a moment to ensure the serial port is fully released
sleep 1

echo "--> Uploading new script (pico_grid.py) to Pico..."
mpremote connect auto cp pico_grid.py :main.py

echo "--> Waiting for Pico to reboot (3 seconds)..."
sleep 3

echo "--> Restarting sensor service..."
sudo systemctl restart sensor.service

echo "--> Update complete. Verifying service status:"
# Wait a final moment for the service to initialize before checking status
sleep 1
sudo systemctl status sensor.service