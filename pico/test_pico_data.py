#!/usr/bin/env python3
"""
Test script to check if Pico H is sending data
"""

import serial
import time

def test_pico_data():
    """Test if Pico H is sending data"""
    try:
        print("🔍 Testing Pico H data transmission...")
        print("Connecting to /dev/ttyACM0...")
        
        ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
        ser.flush()
        
        print("✅ Connected to Pico H")
        print("⏳ Waiting for data (10 seconds)...")
        
        data_received = False
        for i in range(100):  # Check for 10 seconds
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8').rstrip()
                print(f"📡 Received: {line}")
                
                if ',' in line:
                    print(f"✅ Touch matrix data received!")
                    print(f"   Format: {len(line.split(','))} values")
                    data_received = True
                    break
            time.sleep(0.1)
        
        if not data_received:
            print("❌ No data received from Pico H")
            print("\n🔧 Troubleshooting:")
            print("1. Check if Pico H is running MicroPython")
            print("2. Try: mpremote connect auto")
            print("3. Check if pico_grid.py is uploaded as main.py")
            print("4. Try: mpremote connect auto run pico_grid.py")
        
        ser.close()
        return data_received
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_manual_data():
    """Test manual data sending"""
    print("\n🧪 Testing manual data sending...")
    try:
        ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
        
        # Send test data
        test_data = "0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1"
        print(f"📤 Sending test data: {test_data}")
        ser.write((test_data + '\n').encode())
        
        ser.close()
        print("✅ Test data sent")
        
    except Exception as e:
        print(f"❌ Error sending test data: {e}")

if __name__ == "__main__":
    print("🚀 Pico H Data Test")
    print("=" * 40)
    
    # Test if Pico H is sending data
    if test_pico_data():
        print("\n🎉 Pico H is working correctly!")
    else:
        print("\n❌ Pico H is not sending data")
        print("\n🔧 Try these steps:")
        print("1. Upload code: mpremote connect auto cp pico_grid.py :main.py")
        print("2. Check if running: mpremote connect auto")
        print("3. Restart Pico H (unplug and replug USB)")
    
    # Test manual data sending
    test_manual_data()

