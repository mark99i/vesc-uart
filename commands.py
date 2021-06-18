import conv
import datatypes
from uart import UART
from conv import *

class Commands:

    @staticmethod
    def perform_command(uart: UART, command: str, controller_id: int = -1):

        pass

    @staticmethod
    def COMM_GET_VALUES(uart: UART, controller_id: int = -1) -> dict:
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

    @staticmethod
    def COMM_FW_VERSION(uart: UART, controller_id: int = -1) -> dict:
        uart.send_command(datatypes.COMM_Types.COMM_FW_VERSION, controller_id=controller_id)
        result = uart.receive_packet()

        dec = dict() ; i = 0
        dec["fw_version"] = result.data[i]                                   ; i+=1
        dec["fw_version_major"] = result.data[i]                             ; i+=1
        dec["fw_version_minor"] = result.data[i]                             ; i+=1

        # hw_name = result.data[i - 1: result.data[i-1:].find(b'\x00') + 3]
        # dec["hw_name"] = hw_name

        return dec

    @staticmethod
    def scan_can_bus(uart: UART):
        vesc_ids = []

        for i in range(0, 255):
            uart.send_command(datatypes.COMM_Types.COMM_FW_VERSION, controller_id=i)

            try: uart.receive_packet(timeout_ms=20)
            except: continue

            vesc_ids.append(i)

        return vesc_ids

    @staticmethod
    def get_local_controller_id(uart: UART) -> int:
        mask_controller_id = "00000000000000100000000000000000"
        com = conv.binstr_to_bytes(mask_controller_id)

        uart.send_command(datatypes.COMM_Types.COMM_GET_VALUES_SELECTIVE, com)
        result = uart.receive_packet()

        return result.data[4]
