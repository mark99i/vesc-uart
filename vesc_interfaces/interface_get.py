import re
from urllib.parse import urlsplit

from vesc_interfaces.interface import VescInterface

def get_interface_by_path(full_path: str, legacy_speed: int) -> VescInterface:
    result = urlsplit(full_path)

    if result.scheme == "port":
        from vesc_interfaces.lserial import SerialPort
        return SerialPort(full_path)

    if result.scheme == "tcp":
        from vesc_interfaces.tcp import TCPProtocol
        return TCPProtocol(full_path)

    if result.scheme == "pigpio":
        from vesc_interfaces.pigpio import PIGPIO
        return PIGPIO(full_path)

    if result.scheme == "":
        # legacy algo
        IP_PORT_REGEXP = re.compile('[0-9]{3}.[0-9]{3}.[0-9]{3}.[0-9]{3}:[0-9]{5}')

        # network or local device
        if bool(IP_PORT_REGEXP.match(full_path)):
            adr, port = full_path.split(":")
            adr = '.'.join(str(int(part)) for part in adr.split('.'))
            from vesc_interfaces.tcp import TCPProtocol
            return TCPProtocol(f"tcp://{adr}:{port}")
        else:
            from vesc_interfaces.lserial import SerialPort
            return SerialPort(f"port://{full_path}?speed={legacy_speed}")