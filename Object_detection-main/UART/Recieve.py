import serial

# Change COM port and baudrate as needed
PORT = "COM12"       # Windows: COMx, Linux: /dev/ttyUSBx or /dev/ttyACMx
BAUDRATE = 112500

def receive_word():
    with serial.Serial(PORT, BAUDRATE, timeout=1) as ser:
        print("Waiting for data from STM32...")
        while True:
            # Read a line (until newline '\n') or timeout
            data = ser.readline().decode('utf-8').strip()
            if data:
                print(f"Received: {data}")

if __name__ == "__main__":
    receive_word()
