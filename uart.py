import time
from threading import Lock
import serial
from datatypes import COM_States, COMM_Types
import uart_packet

class UART:
    status: COM_States = COM_States.idle
    serial_path: str = None
    serial_speed: int = None

    serial_port = None

    last_error: Exception = None
    debug = False


    multithread_lock = Lock()

    def __init__(self, debug = False):
        self.debug = debug

    def connect(self, com_port_path: str, speed: int, rcv_timeout_ms: int = 0):

        try:
            self.serial_port = serial.Serial(
                port=com_port_path,
                baudrate=speed,
                bytesize=8,
                timeout=rcv_timeout_ms,
                stopbits=serial.STOPBITS_ONE)

            self.serial_path = com_port_path
            self.serial_speed = speed
            self.serial_port.flushInput()
            self.serial_port.flushOutput()

            self.status = COM_States.connected
            return True
        except Exception as e:
            self.status = COM_States.connect_err
            self.last_error = e
            return False

    def send_command(self, command: COMM_Types, data: bytes = bytes(), controller_id: int = -1):
        with self.multithread_lock:
            packet = uart_packet.UART_Packet()
            packet.build_packet(command, data, controller_id)
            if self.debug: print("UART:SND", packet.full.hex())
            self.serial_port.write(packet.full)

    def receive_packet(self, timeout_ms: int = 100, allow_incorrect_crc: bool = False) -> uart_packet.UART_Packet:
        with self.multithread_lock:
            rcvd = bytearray()

            started_op_time_ms = int(time.time() * 1000)
            rcv_need_len = 0

            while True:
                rcvd += self.serial_port.read(300)

                if rcv_need_len == 0 and len(rcvd) > 1:
                    rcv_need_len = rcvd[1] + 4

                op_time_ms = int(time.time() * 1000) - started_op_time_ms
                if op_time_ms > timeout_ms:
                    raise Exception("Timeout receive packet")

                if len(rcvd) > rcv_need_len and rcvd[-1] == 3:
                    break

            packet = uart_packet.UART_Packet().parse(bytes(rcvd), allow_incorrect_crc)
            if self.debug: print("UART:RCV", packet.full.hex())
            return packet
