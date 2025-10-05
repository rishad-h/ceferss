# Simple test version of Pico H code - just sends test data
import machine
import time

# Initialize UART for communication with Raspberry Pi
uart = machine.UART(0, baudrate=115200, tx=machine.Pin(0), rx=machine.Pin(1))

def main():
    """Simple test - just send test data"""
    print("Pico H Test - Sending test data...")
    
    # Test data: first square touched, rest not touched
    test_data = "0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1"
    
    while True:
        # Send test data
        uart.write(test_data + '\n')
        print(f"Sent: {test_data}")
        
        # Wait 1 second
        time.sleep(1)

# Run the main function
if __name__ == "__main__":
    main()

