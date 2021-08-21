import time
from abc import ABC
from urllib.parse import urlsplit, parse_qs

import vesc_interfaces.extern_libs.pigpio as RPI
from vesc_interfaces.interface import VescInterface


class PIGPIO(VescInterface, ABC):
    tx_pin: int = 0
    rx_pin: int = 0

    rx_speed: int = 0
    tx_speed: int = 0

    pi: RPI = None

    # pigpio://?tx=18&rx=20&speed=115200
    # noinspection PyTypeChecker
    def __init__(self, full_path):
        self.full_path = full_path
        self.type = VescInterface.T_GPIO

        result = urlsplit(full_path)
        qs = parse_qs(result.query)

        self.tx_pin = int(qs["tx"][0])
        self.rx_pin = int(qs["rx"][0])
        self.rx_speed = int(qs["speed"][0])
        self.tx_speed = self.rx_speed * 2   # pigpio wtf??

        self.pi = RPI.pi()

    def connect(self):
        self.disconnect()

        self.pi.set_mode(self.rx_pin, RPI.INPUT)
        self.pi.set_mode(self.tx_pin, RPI.OUTPUT)

        self.pi.bb_serial_read_open(self.rx_pin, self.rx_speed)

        self.connected = True

    def receive(self) -> bytes:
        (count, data) = self.pi.bb_serial_read(self.rx_pin)
        if count == 0: return b''
        return data

    def send(self, data: bytes):
        self.pi.wave_clear()
        self.pi.wave_add_serial(self.tx_pin, self.tx_speed, data)
        wid = self.pi.wave_create()

        self.pi.wave_send_once(wid)
        while self.pi.wave_tx_busy(): time.sleep(0.001)

        self.pi.wave_delete(wid)

    def disconnect(self):
        try: self.pi.bb_serial_read_close(self.rx_pin)
        except: pass
        self.pi.set_mode(self.tx_pin, RPI.INPUT)

        self.connected = False

