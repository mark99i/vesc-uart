import datatypes
import conv


class UART_Packet:
    full = None
    body = None
    command: bytes = None
    data = None

    long_packet = False
    crc_ok = False  # only for incoming packets
    final = False

    def parse(self, full: bytes, allow_incorrect_crc: bool = False):
        self.full = full

        if self.long_packet:
            self.body = full[3:-3]
        else:
            self.body = full[2:-3]

        self.command = bytes(self.body[0])
        self.data = self.body[1:]

        incoming_crc = int.from_bytes(full[-3:-1], byteorder="big")
        need_crc = conv.crc16(self.body)
        self.crc_ok = need_crc == incoming_crc

        if not self.crc_ok and not allow_incorrect_crc:
            raise Exception("Incoming packet have incorrect CRC (" + str(need_crc) + " != " + str(incoming_crc) + ")")

        return self

    def build_packet(self, command: datatypes.COMM_Types, data: bytes = bytes(), controller_id: int = -1):
        self.command = conv.uint8_to_bytes(command.value)

        self.body = bytearray()
        if controller_id != -1:
            # using COMM_FORWARD_CAN for request to another VESC, connected over CAN
            self.body += conv.uint8_to_bytes(datatypes.COMM_Types.COMM_FORWARD_CAN.value)
            self.body += conv.uint8_to_bytes(controller_id)
        self.body += self.command     # command (1 byte)
        self.body += data             # data

        p_len = len(self.body)
        self.long_packet = p_len > 255

        self.full = bytearray()
        if self.long_packet:
            self.full += bytes([0x03])                  # start byte (for long packet)
            self.full += conv.uint16_to_bytes(p_len)    # packet len byte (for long packet 2 bytes)
        else:
            self.full += bytes([0x02])                  # start byte
            self.full += bytes([p_len])                 # packet len byte

        self.full += self.body                              # packet body
        self.full += conv.crc16_as_uint16(bytes(self.body)) # crc
        self.full += bytes([0x03])                          # end byte




