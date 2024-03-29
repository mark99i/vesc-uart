from abc import ABC
from urllib.parse import urlsplit, parse_qs

from serial import Serial, STOPBITS_ONE
from vesc_interfaces.interface import VescInterface

class SerialPort(VescInterface, ABC):
    device: str = ""
    speed: int = 0

    port: Serial = None

    # port:///dev/ttyUSB0?speed=115200
    def __init__(self, full_path):
        self.full_path = full_path
        self.type = VescInterface.T_GPIO

        result = urlsplit(full_path)
        self.device = result.path

        qs = parse_qs(result.query)
        self.speed = int(qs["speed"][0])

    def connect(self):
        self.port = Serial(
            port=self.device,
            baudrate=self.speed,
            bytesize=8,
            timeout=0,
            stopbits=STOPBITS_ONE)

        self.port.flushInput()
        self.port.flushOutput()

        pass

    def receive(self):
        return self.port.read(1000)

    def send(self, data: bytes):
        self.port.write(data)

    def disconnect(self):
        self.port.close()
