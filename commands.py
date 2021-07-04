import base64
import traceback

import commands_configuration
import conv
import datatypes
from uart import UART
from conv import *

class Commands:
    SCAN_CAN = "SCAN_CAN"
    LOCAL_ID = "LOCAL_ID"

    stats = {"success": 0, "fail_timeout": 0, "fail_crc": 0, "failed_other": 0}

    # noinspection PyTypeChecker
    def perform_command(self, uart: UART, command: str, controller_id: int = -1, args: dict = None) -> dict:
        try:
            result: dict = None

            if command == "SCAN_CAN":
                result = {"ids": self.scan_can_bus(uart)}

            if command == "LOCAL_ID":
                result = {"id": self.get_local_controller_id(uart)}

            if command == "COMM_GET_VALUES":
                result = self.COMM_GET_VALUES(uart, controller_id)
        
            if command == "COMM_FW_VERSION":
                result = self.COMM_FW_VERSION(uart, controller_id)

            if command == "COMM_SET_CURRENT_BRAKE":
                self.COMM_SET_CURRENT_BRAKE(uart, args, controller_id)         # data: {"current": "0"}
                result = dict()

            if command == "COMM_GET_MCCONF":
                result = self.COMM_GET_MCCONF(uart, controller_id, args)       # data: {"need_bin": False}

            self.stats["success"] += 1
            return result
        except Exception as e:
            if   "Timeout receive packet" in str(e):
                self.stats["fail_timeout"] += 1
            elif "incorrect CRC" in str(e):
                self.stats["fail_crc"] += 1
            else:
                self.stats["failed_other"] += 1

            print("Exception in perform_command")
            print(traceback.format_exc())
            print()
            return None

    def COMM_GET_VALUES(self, uart: UART, controller_id: int = -1) -> dict:
        uart.send_command(datatypes.COMM_Types.COMM_GET_VALUES, controller_id=controller_id)
        result = uart.receive_packet()

        dec = dict() ; i = 0
        dec["temp_fet_filtered"] = float_from_bytes(result.data[i : i+2])       ; i+=2
        dec["temp_motor_filtered"] = float_from_bytes(result.data[i : i+2])     ; i+=2

        dec["avg_motor_current"] = float_from_bytes(result.data[i : i+4], 1e2)  ; i+=4
        dec["avg_input_current"] = float_from_bytes(result.data[i : i+4], 1e2)  ; i+=4
        dec["avg_id"] = float_from_bytes(result.data[i : i+4], 1e2)             ; i+=4
        dec["avg_iq"] = float_from_bytes(result.data[i : i+4], 1e2)             ; i+=4

        dec["duty_cycle"] = float_from_bytes(result.data[i : i+2], 1e3)         ; i+=2
        dec["rpm"] = float_from_bytes(result.data[i : i+4], 1e0)                ; i+=4
        dec["voltage"] = float_from_bytes(result.data[i : i+2], 1e1)            ; i+=2

        dec["amp_hours"] = float_from_bytes(result.data[i : i+4], 1e4)          ; i+=4
        dec["amp_hours_charged"] = float_from_bytes(result.data[i : i+4], 1e4)  ; i+=4

        dec["watt_hours"] = float_from_bytes(result.data[i : i+4], 1e4)         ; i+=4
        dec["watt_hours_charged"] = float_from_bytes(result.data[i : i+4], 1e4) ; i+=4

        dec["tachometer"] = uint_from_bytes(result.data[i : i+4])               ; i+=4
        dec["tachometer_abs"] = uint_from_bytes(result.data[i : i+4])           ; i+=4

        dec["fault_code"] = result.data[i]                                      ; i+=1
        dec["fault_code_desc"] = datatypes.FAULT_Codes(dec["fault_code"]).name

        dec["pid_pos"] = float_from_bytes(result.data[i : i+4], 1e6)            ; i+=4

        dec["controller_id"] = result.data[i]                                   ; i+=1

        dec["temp_mos1"] = float_from_bytes(result.data[i : i+2], 1e1)          ; i+=2
        dec["temp_mos2"] = float_from_bytes(result.data[i : i+2], 1e1)          ; i+=2
        dec["temp_mos3"] = float_from_bytes(result.data[i : i+2], 1e1)          ; i+=2

        dec["avg_vd"] = float_from_bytes(result.data[i : i+4], 1e3)             ; i+=4
        dec["avg_vq"] = float_from_bytes(result.data[i : i+4], 1e3)             ; i+=4

        return dec

    def COMM_FW_VERSION(self, uart: UART, controller_id: int = -1) -> dict:
        uart.send_command(datatypes.COMM_Types.COMM_FW_VERSION, controller_id=controller_id)
        result = uart.receive_packet()

        dec = dict() ; i = 0
        dec["fw_version"] = result.data[i]          ; i += 1
        dec["fw_version_major"] = result.data[i]    ; i += 1
        dec["fw_version_minor"] = result.data[i]    ; i += 1

        dec["fw_version_generic"] = float(str(dec.get("fw_version")) + "." + str(dec.get("fw_version_major")))

        model = result.data[i-1:]
        model_end = model.find(bytes([0x00]))
        model = model[:model_end]
        dec["hw_name"] = model.decode()
        i += model_end

        uuid = result.data[i:i+12]
        dec["mc_uuid"] = uuid.hex()
        i += 12

        dec["pairing_done"] = result.data[i]        ; i += 1
        dec["test_ver_number"] = result.data[i]     ; i += 1
        dec["hw_type_vesc"] = result.data[i]        ; i += 1
        return dec

    def COMM_SET_CURRENT_BRAKE(self, uart: UART, args: dict, controller_id: int = -1) -> None:
        current = args["current"]

        current = current * 1000
        data = uint32_to_bytes(current)

        uart.send_command(datatypes.COMM_Types.COMM_SET_CURRENT, controller_id=controller_id, data=data)
        return None

    def COMM_GET_APPCONF(self, uart: UART, controller_id: int = -1) -> dict:
        uart.send_command(datatypes.COMM_Types.COMM_GET_APPCONF, controller_id=controller_id)
        result = uart.receive_packet(timeout_ms=300)

        #print(result.data)
        #print(result.data.hex())
        return {"not_parsed_data": base64.b64encode(result.data).decode()}

    def COMM_GET_MCCONF(self, uart: UART, controller_id: int = -1, args=None) -> dict:
        if args is None: args = {"need_bin": False}
        need_bin = args.get("need_bin", False)

        fw = self.COMM_FW_VERSION(uart, controller_id)

        uart.send_command(datatypes.COMM_Types.COMM_GET_MCCONF, controller_id=controller_id)
        result = uart.receive_packet(timeout_ms=400)

        ok, result = commands_configuration.deserialize_mcconf(result, fw["fw_version_generic"], need_bin)
        return result

    def COMM_REBOOT(self, uart: UART, controller_id: int = -1) -> None:
        uart.send_command(datatypes.COMM_Types.COMM_REBOOT, controller_id=controller_id)
        return None

    def scan_can_bus(self, uart: UART):
        vesc_ids = []

        for i in range(0, 255):
            uart.send_command(datatypes.COMM_Types.COMM_FW_VERSION, controller_id=i)

            try: uart.receive_packet(timeout_ms=20)
            except: continue

            vesc_ids.append(i)

        return vesc_ids

    def get_local_controller_id(self, uart: UART) -> int:
        mask_controller_id = "00000000 00000010 00000000 00000000"
        com = conv.binstr_to_bytes(mask_controller_id)

        uart.send_command(datatypes.COMM_Types.COMM_GET_VALUES_SELECTIVE, com)
        result = uart.receive_packet()

        return result.data[4]
