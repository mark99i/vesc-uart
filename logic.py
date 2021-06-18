import datatypes
import uart
from network_packet import RequestPacket
from commands import Commands

class Logic:
    uart = None
    local_vesc_id = -1

    def work_packet(self, packet: RequestPacket) -> dict:
        if packet.api_endpoint == "/uart/status":
            if self.uart is None:
                return {"success": True, "status": "not_configured"}
            else:
                return {"success": True, "status": self.uart.status.name, "speed": self.uart.serial_speed,
                        "path": self.uart.serial_path, "last_err": self.uart.last_error,
                        "debug_enabled": self.uart.debug}

        if packet.api_endpoint == "/uart/connect":
            if self.uart is not None and self.uart.status == datatypes.COM_States.connected:
                self.uart.serial_port.close()

            self.uart = uart.UART(bool(packet.json_root.get("debug_enabled", False)))
            connect_result = self.uart.connect(packet.json_root["path"], int(packet.json_root["speed"]))

            if connect_result:
                return {"success": True, "status": self.uart.status.name}
            else:
                return {"success": False, "status": self.uart.status.name, "last_err": uart.UART.last_error,
                        "message": "uart_connection_error"}

        if self.uart is None or self.uart.status != datatypes.COM_States.connected:
            return {"success": False, "message": "need_serial_connection_setup"}




        if packet.api_endpoint == "/vesc/local/id":
            vesc_id = Commands.get_local_controller_id(self.uart)
            return {"success": True, "controller_id": vesc_id}

        if packet.api_endpoint == "/vesc/local/can/scan":
            vesc_ids_on_bus = Commands.scan_can_bus(self.uart)
            return {"success": True, "vesc_ids_on_bus": vesc_ids_on_bus}


        if packet.api_endpoint.startswith("/vesc/"):
            packet.api_endpoint = packet.api_endpoint[6:]
            vesc_id = packet.api_endpoint[ : packet.api_endpoint.find("/")]
            if vesc_id == "local" or vesc_id == self.local_vesc_id: vesc_id = -1
            vesc_id = int(vesc_id)
            packet.api_endpoint = packet.api_endpoint[packet.api_endpoint.find("/"):]

            if packet.api_endpoint.startswith("/command/"):
                command = packet.api_endpoint[9:]
                data = Commands.perform_command(self.uart, command, vesc_id)
                if data is not None:
                    return {"success": True, "data": data}

        pass