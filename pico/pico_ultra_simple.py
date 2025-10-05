# Ultra simple test - just print and send one message
import machine
import time

print("Starting ultra simple test...")

# Initialize UART
uart = machine.UART(0, baudrate=115200, tx=machine.Pin(0), rx=machine.Pin(1))
print("UART initialized")

# Send one test message
test_message = "Hello from Pico H"
uart.write(test_message + '\n')
print(f"Sent: {test_message}")

# Wait a bit
time.sleep(1)

# Send another message
uart.write("Test message 2\n")
print("Sent: Test message 2")

print("Ultra simple test complete")

