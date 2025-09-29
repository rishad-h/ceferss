#!/usr/bin/env python3
"""
Test script to check OLED display and serial communication
"""

import serial
import time
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import sh1106
from PIL import ImageDraw

def test_serial():
    """Test serial communication with Pico H"""
    print("🔍 Testing serial communication...")
    
    try:
        ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
        ser.flush()
        
        print("✅ Serial port opened successfully")
        
        # Wait for data
        print("⏳ Waiting for data from Pico H...")
        for i in range(10):  # Try for 10 seconds
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8').rstrip()
                print(f"📡 Received: {line}")
                if ',' in line:
                    print("✅ Touch matrix data received!")
                    return True
            time.sleep(1)
        
        print("❌ No data received from Pico H")
        return False
        
    except Exception as e:
        print(f"❌ Serial error: {e}")
        return False
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()

def test_oled():
    """Test OLED display"""
    print("\n🔍 Testing OLED display...")
    
    try:
        # Try to initialize OLED
        i2c_bus = i2c(port=1, address=0x3C)
        device = sh1106(i2c_bus, rotate=0)
        device.clear()
        
        print("✅ OLED initialized successfully")
        
        # Draw a test pattern
        with canvas(device) as draw:
            draw.text((10, 10), "OLED Test", fill="white")
            draw.text((10, 30), "Working!", fill="white")
            draw.rectangle((10, 50, 100, 70), outline="white", fill="white")
        
        print("✅ OLED test pattern drawn")
        return True
        
    except Exception as e:
        print(f"❌ OLED error: {e}")
        print("Check I2C connections and address")
        return False

def test_i2c():
    """Test I2C without sudo"""
    print("\n🔍 Testing I2C...")
    
    try:
        # Try to scan I2C bus
        import smbus
        bus = smbus.SMBus(1)
        
        print("Scanning I2C devices...")
        devices = []
        for addr in range(0x3C, 0x3D):  # Check around 0x3C
            try:
                bus.read_byte(addr)
                devices.append(hex(addr))
                print(f"✅ Found device at {hex(addr)}")
            except:
                pass
        
        if devices:
            print(f"✅ I2C devices found: {devices}")
            return True
        else:
            print("❌ No I2C devices found")
            return False
            
    except Exception as e:
        print(f"❌ I2C error: {e}")
        return False

def main():
    print("🧪 Pico H + OLED Test Suite")
    print("=" * 40)
    
    # Test serial communication
    serial_ok = test_serial()
    
    # Test I2C
    i2c_ok = test_i2c()
    
    # Test OLED
    oled_ok = test_oled()
    
    print("\n" + "=" * 40)
    print("📊 Test Results:")
    print(f"Serial Communication: {'✅' if serial_ok else '❌'}")
    print(f"I2C Bus: {'✅' if i2c_ok else '❌'}")
    print(f"OLED Display: {'✅' if oled_ok else '❌'}")
    
    if not serial_ok:
        print("\n🔧 Serial Issues:")
        print("- Check Pico H is running MicroPython")
        print("- Try: mpremote connect auto")
        print("- Check port: ls /dev/tty*")
    
    if not i2c_ok:
        print("\n🔧 I2C Issues:")
        print("- Check I2C connections (SDA, SCL)")
        print("- Enable I2C: sudo raspi-config")
        print("- Check with: sudo i2cdetect -y 1")
    
    if not oled_ok:
        print("\n🔧 OLED Issues:")
        print("- Check I2C address (should be 0x3C)")
        print("- Check power connections")
        print("- Try different I2C port")

if __name__ == "__main__":
    main()
