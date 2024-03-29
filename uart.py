import re
import socket
import time
from threading import Lock
import serial
import traceback

import conv
from datatypes import COM_States, COMM_Types
import uart_packet
from vesc_interfaces.interface import VescInterface
from vesc_interfaces.interface_get import get_interface_by_path


class UART:
    status: COM_States = COM_States.idle

    interface: VescInterface = None

    last_error: Exception = None
    debug = False
    rcv_timeout_ms: int = 100
    need_drop_buffers: bool = False

    multithread_lock: Lock

    def __init__(self, debug = False):
        self.debug = debug
        self.interface = None
        self.multithread_lock = Lock()

    # noinspection PyTypeChecker
    def connect(self, path: str, legacy_speed: int, rcv_timeout_ms: int = 100):
        self.rcv_timeout_ms = rcv_timeout_ms
        try:
            if self.interface is not None and self.interface.connected:
                self.interface.disconnect()

            self.interface = get_interface_by_path(path, legacy_speed)
            self.interface.connect()

            self.status = COM_States.connected
            return True
        except Exception as e:
            self.interface = None
            self.status = COM_States.connect_err
            self.last_error = e

            print("Exception in UART->connect")
            print(traceback.format_exc())
            return False

    def send_command(self, command: COMM_Types, data: bytes = bytes(), controller_id: int = -1):
        with self.multithread_lock:
            if self.need_drop_buffers:
                if self.debug: print("UART:Perform receive buffer drop after timeout error")
                time.sleep(0.2)
                self.interface.receive()
                self.need_drop_buffers = False

            packet = uart_packet.UART_Packet()
            packet.build_packet(command, data, controller_id)
            if self.debug: print("UART:SND (h)", packet.full.hex())
            if self.debug: print("UART:SND (b)", packet.full)

            self.interface.send(packet.full)

    def receive_packet(self, timeout_ms: int = rcv_timeout_ms, allow_incorrect_crc: bool = False) -> uart_packet.UART_Packet:
        with self.multithread_lock:
            rcvd = bytearray()

            started_op_time_ms = int(time.time() * 1000)
            long_packet = False

            rcv_need_len = 0

            if self.interface.type == self.interface.T_TCP:
                timeout_ms += 300

            while True:
                rcvd += self.interface.receive()

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
                    self.need_drop_buffers = True
                    raise Exception("Timeout receive packet")

            packet = uart_packet.UART_Packet()
            packet.long_packet = long_packet
            packet.parse(bytes(rcvd), allow_incorrect_crc)
            if self.debug: print("UART:RCV (h)", packet.full.hex())
            if self.debug: print("UART:RCV (b)", packet.full)
            return packet
