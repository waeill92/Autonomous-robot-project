import serial
import time

# Change this to match your COM port (Windows: COMx, Linux: /dev/ttyUSBx or /dev/ttyACMx)
PORT = "COM12"
BAUDRATE = 112500

def send_char(ch):
    with serial.Serial(PORT, BAUDRATE, timeout=1) as ser:
        ser.write(ch.encode('utf-8'))
        print(f"Sent: {ch}")
        time.sleep(0.1)

if __name__ == "__main__":
    while True:
        send_char("b")
        # choice = input("Enter 'a' or 'b' to send (q to quit): ").strip().lower()
        # if choice in ["a", "b"]:
        #     send_char("a")
        # elif choice == "q":
        #     break
        # else:
        #     print("Invalid input. Please type 'a', 'b', or 'q'.")
