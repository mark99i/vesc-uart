import serial
import time
from s import *

serialPort = serial.Serial(
    port="COM4", baudrate=115200, bytesize=8, timeout=0, stopbits=serial.STOPBITS_ONE
)
time.sleep(1)


command = bytearray()
command += bytes([0x32])    # command COMM_GET_VALUES_SELECTIVE (int 50)
command += bytes([0x00])     # filter mask 1
command += bytes([0x00])     # filter mask 2
command += bytes([0x00])     # filter mask 3
command += bytes([0x01])     # filter mask 4

crc = crc16(bytes(command))
crc = crc.to_bytes(2, byteorder='big')

packet = bytearray([0x02])      # start byte
packet += bytes([len(command)]) # packet len byte
packet += command               # packet body
packet += crc                   # crc
packet += bytes([0x03])         # end byte

data = bytes(packet)
print(data.hex(sep=" "))

time.sleep(1)
print("started")


while 1:
    sended = int(time.time() * 1000)
    serialString = bytearray()

    serialPort.write(data)
    # Wait until there is data waiting in the serial buffer
    while serialPort.in_waiting == 0:
        time.sleep(0.0001)


    serialString += serialPort.readline()
    while not str(serialString.hex()).endswith("03"):
        while serialPort.in_waiting == 0:
            time.sleep(0.0001)
        serialString += serialPort.readline()

    packet_body = serialString[2:-3]
    packet_crc = crc16(packet_body)

    if packet_crc == int.from_bytes(serialString[-3:-1], byteorder="big"):
        print("CRC OK  ", end="")
    else:
        print("CRC ERR ", end="")


    temp = float16_from_bytes(serialString[-5:-3])

    print(int((time.time() * 1000) - sended), "temp =", temp)

    time.sleep(0.3)