# Minimal test - just send all 1s continuously
import machine
import time

# Initialize UART
uart = machine.UART(0, baudrate=115200, tx=machine.Pin(0), rx=machine.Pin(1))

def main():
    print("Pico H Minimal Test - Sending all 1s")
    
    while True:
        # Send all 1s (no touch detected)
        data = "1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1"
        uart.write(data + '\n')
        print(f"Sent: {data}")
        time.sleep(0.1)  # Send every 100ms

if __name__ == "__main__":
    main()

