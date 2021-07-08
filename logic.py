import datatypes
import uart
from network_packet import RequestPacket
from commands import Commands

class Logic:
    uart = None
    vesc = Commands()
    local_id = -1

    def work_packet(self, packet: RequestPacket) -> dict:
        if self.uart is not None and self.uart.debug:
            print("received request:", packet.__dict__)

        # get service/uart status and stats
        if packet.api_endpoint == "/uart/status":
            if self.uart is None:
                return {"success": True, "status": "not_configured", "stats": self.vesc.stats}
            else:
                res = self.vesc.perform_command(self.uart, Commands.LOCAL_ID)
                if res is not None: self.local_id = int(res.get("id"))

                return {"success": True, "status": self.uart.status.name, "speed": self.uart.serial_speed,
                        "path": self.uart.serial_path, "last_err": str(self.uart.last_error),
                        "debug_enabled": self.uart.debug, "local_id": self.local_id, "stats": self.vesc.stats}

        # connecting to serial port
        if packet.api_endpoint == "/uart/connect":
            self.uart = uart.UART(bool(packet.json_root.get("debug_enabled", False)))
            connect_result = self.uart.connect(packet.json_root["path"], int(packet.json_root["speed"]), packet.json_root.get("rcv_timeout_ms", 100))

            if connect_result:
                return {"success": True, "status": self.uart.status.name}
            else:
                return {"success": False, "status": self.uart.status.name, "last_err": str(uart.UART.last_error),
                        "message": "uart_connection_error"}

        if self.uart is None or self.uart.status != datatypes.COM_States.connected:
            return {"success": False, "message": "serial_not_configured"}

        # commands to vesc
        if packet.api_endpoint == "/vesc/local/id":
            res = self.vesc.perform_command(self.uart, Commands.LOCAL_ID)
            if res is None: return {"success": False, "message": "unknown_command_or_error"}
            return {"success": True, "controller_id": int(res.get("id"))}

        if packet.api_endpoint == "/vesc/local/can/scan":
            res = self.vesc.perform_command(self.uart, Commands.SCAN_CAN)
            if res is None: return {"success": False, "message": "unknown_command_or_error"}
            return {"success": True, "vesc_ids_on_bus": res.get("ids")}

        if packet.api_endpoint.startswith("/vescs/command/"):
            command = packet.api_endpoint[15:]
            args = packet.json_root.get("args")
            vesc_ids = packet.json_root.get("vesc_ids", None)
            vesc_id_one = packet.json_root.get("vesc_id", None)
            if vesc_ids is None and vesc_id_one is not None:
                vesc_ids = [vesc_id_one]

            answer = {"command": command, "args": args, "success": False, "data": {}}
            for vesc_id in vesc_ids:
                if int(vesc_id) < 0: vesc_id = -1
                comm_result = self.vesc.perform_command(self.uart, command, vesc_id, packet.json_root.get("args"))

                if comm_result is None: return {"success": False, "message": "unknown_command_or_error"}
                answer["data"][vesc_id] = comm_result
            answer["success"] = True
            return answer

        pass