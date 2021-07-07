import re
import socket
import time
from threading import Lock
import serial
import traceback

import conv
from datatypes import COM_States, COMM_Types
import uart_packet

class UART:
    status: COM_States = COM_States.idle
    serial_path: str = None
    serial_speed: int = None

    serial_port: serial.Serial = None
    network_port: socket.socket = None

    last_error: Exception = None
    debug = False
    rcv_timeout_ms: int = 100

    IP_PORT_REGEXP = re.compile('[0-9]{3}.[0-9]{3}.[0-9]{3}.[0-9]{3}:[0-9]{5}')

    multithread_lock = Lock()

    def __init__(self, debug = False):
        self.debug = debug

    # noinspection PyTypeChecker
    def connect(self, com_port_path: str, speed: int, rcv_timeout_ms: int = 100):

        self.rcv_timeout_ms = rcv_timeout_ms
        try:
            if self.network_port is not None:
                try:
                    self.network_port.shutdown(socket.SHUT_RDWR)
                    self.network_port.close()
                finally:
                    self.network_port = None

            if self.serial_port is not None and bool(self.serial_port.is_open):
                self.serial_port.close()
                self.serial_port = None

            if bool(self.IP_PORT_REGEXP.match(com_port_path)):
                adr, port = com_port_path.split(":")
                adr = '.'.join(str(int(part)) for part in adr.split('.'))
                self.network_port = socket.socket()
                self.network_port.connect((adr, int(port)))
                self.network_port.settimeout(rcv_timeout_ms + 0.001)
                self.network_port.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                self.network_port.setblocking(False)

            else:
                self.serial_port = serial.Serial(
                    port=com_port_path,
                    baudrate=speed,
                    bytesize=8,
                    timeout=0,
                    stopbits=serial.STOPBITS_ONE)

                self.serial_path = com_port_path
                self.serial_speed = speed
                self.serial_port.flushInput()
                self.serial_port.flushOutput()

            self.status = COM_States.connected
            return True
        except Exception as e:
            self.serial_port = None
            self.network_port = None
            self.status = COM_States.connect_err
            self.last_error = e

            print("Exception in UART->connect")
            print(traceback.format_exc())
            return False

    def send_command(self, command: COMM_Types, data: bytes = bytes(), controller_id: int = -1):
        with self.multithread_lock:
            packet = uart_packet.UART_Packet()
            packet.build_packet(command, data, controller_id)
            if self.debug: print("UART:SND (h)", packet.full.hex())
            if self.debug: print("UART:SND (b)", packet.full)

            if self.network_port is not None:
                self.network_port.sendall(packet.full)
            else:
                self.serial_port.write(packet.full)

    def __receive_network(self, p_size: int) -> bytearray:
        rcvd = bytearray()
        try:
            rcvd += self.network_port.recv(p_size)
        except:
            pass
        return rcvd

    def receive_packet(self, timeout_ms: int = rcv_timeout_ms, allow_incorrect_crc: bool = False) -> uart_packet.UART_Packet:
        with self.multithread_lock:
            rcvd = bytearray()

            started_op_time_ms = int(time.time() * 1000)
            long_packet = False

            rcv_need_len = 0

            if self.network_port is not None:
                timeout_ms += 200

            while True:
                if self.network_port is not None:
                    rcvd += self.__receive_network(1000)
                else:
                    rcvd += self.serial_port.read(300)

                if rcv_need_len == 0 and len(rcvd) > 3:
                    if rcvd[0] == 2:
                        rcv_need_len = rcvd[1] + 4
                    else:
                        long_packet = True
                        rcv_need_len = conv.uint_from_bytes(rcvd[1:3]) + 4

                if len(rcvd) > rcv_need_len and rcvd[-1] == 3:
                    break

                op_time_ms = int(time.time() * 1000) - started_op_time_ms
                if op_time_ms > timeout_ms:
                    raise Exception("Timeout receive packet")

            packet = uart_packet.UART_Packet()
            packet.long_packet = long_packet
            packet.parse(bytes(rcvd), allow_incorrect_crc)
            if self.debug: print("UART:RCV (h)", packet.full.hex())
            if self.debug: print("UART:RCV (b)", packet.full)
            return packet
