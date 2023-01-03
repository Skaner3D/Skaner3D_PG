import serial
import time


ser = serial.Serial("/dev/ttyS0", 9600)

while True:        
    msg = 1
    ser.write(msg.to_bytes(1, 'big'))
    print("TX:", msg)
    received_data = ser.read()
    received_data_int = int.from_bytes(received_data, 'big')
    print("RX: ", received_data_int)
    time.sleep(1)