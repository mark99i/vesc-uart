import socket
from abc import ABC
from urllib.parse import urlsplit, parse_qs

import socket
from vesc_interfaces.interface import VescInterface

class TCPProtocol(VescInterface, ABC):
    net_ip: str = ""
    net_port: int = 0

    port: socket.socket = None

    # tcp://192.168.1.10:65102
    def __init__(self, full_path):
        self.full_path = full_path

        result = urlsplit(full_path)
        self.net_ip = str(result.hostname)
        self.net_port = int(result.port)

        self.port = socket.socket()

    def connect(self):
        self.port.connect((self.net_ip, self.net_port))
        self.port.settimeout(self.receive_timeout_ms + 1)
        self.port.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.port.setblocking(False)
        pass

    def receive(self):
        rcvd = bytearray()
        try: rcvd += self.port.recv(1000)
        except: pass
        return rcvd

    def send(self, data: bytes):
        self.port.sendall(data)
        pass

    def disconnect(self):
        self.port.shutdown(socket.SHUT_RDWR)
        self.port.close()
