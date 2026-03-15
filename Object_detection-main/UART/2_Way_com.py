import serial

PORT = "COM12"     # Adjust for your system
BAUDRATE = 112500

def uart_communicate():
    with serial.Serial(PORT, BAUDRATE, timeout=1) as ser:
        print("Listening for STM32...")

        while True:
            # Read line from STM32
            data = ser.readline().decode('utf-8').strip()
            if data:
                print(f"Received from STM32: {data}")

                # If STM32 sent "digit", reply with "9"
                if data == "digit":
                    ser.write(b'9')
                    print("Sent back: 9")

if __name__ == "__main__":
    uart_communicate()
