import base64
import traceback

from conv import *
from uart_packet import UART_Packet

def deserialize_mcconf(result: UART_Packet, fw_ver: float, need_bin = False) -> tuple[bool, dict]:
    ok = False
    dec = dict()
    try:
        if fw_ver == 5.2:
            dec["mcconf"] = deserialize_mcconf_fw52(result)

        if dec.get("mcconf") is None:
            dec["error_msg"] = "unknown_version_fw"
        else:
            ok = True
    except Exception:
        dec["error_msg"] = "exception_on_decoding"
        print("Exceprion in deserialize_mcconf")
        print(traceback.format_exc())

    if need_bin:
        dec["format_bin"] = base64.b64encode(result.data).decode()

    return ok, dec

def deserialize_mcconf_fw52(result: UART_Packet) -> dict:
    dec = dict(); i = 0
    dec["MCCONF_SIGNATURE"] = uint_from_bytes(result.data[i: i + 4])    ; i += 4
    dec["pwm_mode"] = result.data[i]           ; i += 1
    dec["comm_mode"] = result.data[i]          ; i += 1
    dec["motor_type"] = result.data[i]         ; i += 1
    dec["sensor_mode"] = result.data[i]        ; i += 1
    dec["l_current_max"] = float32_from_bytes_auto(result.data[i: i + 4])       ; i += 4
    dec["l_current_min"] = float32_from_bytes_auto(result.data[i: i + 4])       ; i += 4
    dec["l_in_current_max"] = float32_from_bytes_auto(result.data[i: i + 4])    ; i += 4
    dec["l_in_current_min"] = float32_from_bytes_auto(result.data[i: i + 4])    ; i += 4
    dec["l_abs_current_max"] = float32_from_bytes_auto(result.data[i: i + 4])   ; i += 4
    dec["l_min_erpm"] = float32_from_bytes_auto(result.data[i: i + 4])      ; i += 4
    dec["l_max_erpm"] = float32_from_bytes_auto(result.data[i: i + 4])      ; i += 4
    dec["l_erpm_start"] = float32_from_bytes_auto(result.data[i: i + 4])    ; i += 4
    dec["l_max_erpm_fbrake"] = float32_from_bytes_auto(result.data[i: i + 4])   ; i += 4
    dec["l_max_erpm_fbrake_cc"] = float32_from_bytes_auto(result.data[i: i + 4])   ; i += 4
    dec["l_min_vin"] = float32_from_bytes_auto(result.data[i: i + 4])       ; i += 4
    dec["l_max_vin"] = float32_from_bytes_auto(result.data[i: i + 4])       ; i += 4
    dec["l_battery_cut_start"] = float32_from_bytes_auto(result.data[i: i + 4]) ; i += 4
    dec["l_battery_cut_end"] = float32_from_bytes_auto(result.data[i: i + 4])   ; i += 4

    dec["l_slow_abs_current"] = result.data[i]                  ; i += 1

    dec["l_temp_fet_start"] = float32_from_bytes_auto(result.data[i: i + 4])    ; i += 4
    dec["l_temp_fet_end"] = float32_from_bytes_auto(result.data[i: i + 4])      ; i += 4
    dec["l_temp_motor_start"] = float32_from_bytes_auto(result.data[i: i + 4])  ; i += 4
    dec["l_temp_motor_end"] = float32_from_bytes_auto(result.data[i: i + 4])    ; i += 4
    dec["l_temp_accel_dec"] = float32_from_bytes_auto(result.data[i: i + 4])    ; i += 4
    dec["l_min_duty"] = float32_from_bytes_auto(result.data[i: i + 4])      ; i += 4
    dec["l_max_duty"] = float32_from_bytes_auto(result.data[i: i + 4])      ; i += 4
    dec["l_watt_max"] = float32_from_bytes_auto(result.data[i: i + 4])      ; i += 4
    dec["l_watt_min"] = float32_from_bytes_auto(result.data[i: i + 4])      ; i += 4
    dec["l_current_max_scale"] = float32_from_bytes_auto(result.data[i: i + 4]) ; i += 4
    dec["l_current_min_scale"] = float32_from_bytes_auto(result.data[i: i + 4]) ; i += 4
    dec["l_duty_start"] = float32_from_bytes_auto(result.data[i: i + 4])    ; i += 4
    dec["sl_min_erpm"] = float32_from_bytes_auto(result.data[i: i + 4])             ; i += 4
    dec["sl_min_erpm_cycle_int_limit"] = float32_from_bytes_auto(result.data[i: i + 4])     ; i += 4
    dec["sl_max_fullbreak_current_dir_change"] = float32_from_bytes_auto(result.data[i: i + 4]) ; i += 4
    dec["sl_cycle_int_limit"] = float32_from_bytes_auto(result.data[i: i + 4])          ; i += 4
    dec["sl_phase_advance_at_br"] = float32_from_bytes_auto(result.data[i: i + 4])          ; i += 4
    dec["sl_cycle_int_rpm_br"] = float32_from_bytes_auto(result.data[i: i + 4])         ; i += 4
    dec["sl_bemf_coupling_k"] = float32_from_bytes_auto(result.data[i: i + 4])          ; i += 4

    dec["hall_table"] = dict()
    dec["hall_table"][0] = result.data[i]   ; i += 1
    dec["hall_table"][1] = result.data[i]   ; i += 1
    dec["hall_table"][2] = result.data[i]   ; i += 1
    dec["hall_table"][3] = result.data[i]   ; i += 1
    dec["hall_table"][4] = result.data[i]   ; i += 1
    dec["hall_table"][5] = result.data[i]   ; i += 1
    dec["hall_table"][6] = result.data[i]   ; i += 1
    dec["hall_table"][7] = result.data[i]   ; i += 1

    dec["hall_sl_erpm"] = float32_from_bytes_auto(result.data[i: i + 4])        ; i += 4
    dec["foc_current_kp"] = float32_from_bytes_auto(result.data[i: i + 4])          ; i += 4
    dec["foc_current_ki"] = float32_from_bytes_auto(result.data[i: i + 4])          ; i += 4
    dec["foc_f_sw"] = float32_from_bytes_auto(result.data[i: i + 4])            ; i += 4
    dec["foc_dt_us"] = float32_from_bytes_auto(result.data[i: i + 4])           ; i += 4

    dec["foc_encoder_inverted"] = result.data[i]                    ; i += 1

    dec["foc_encoder_offset"] = float32_from_bytes_auto(result.data[i: i + 4])      ; i += 4
    dec["foc_encoder_ratio"] = float32_from_bytes_auto(result.data[i: i + 4])       ; i += 4
    dec["foc_encoder_sin_gain"] = float32_from_bytes_auto(result.data[i: i + 4])    ; i += 4
    dec["foc_encoder_cos_gain"] = float32_from_bytes_auto(result.data[i: i + 4])    ; i += 4
    dec["foc_encoder_sin_offset"] = float32_from_bytes_auto(result.data[i: i + 4])      ; i += 4
    dec["foc_encoder_cos_offset"] = float32_from_bytes_auto(result.data[i: i + 4])          ; i += 4
    dec["foc_encoder_sincos_filter_constant"] = float32_from_bytes_auto(result.data[i: i + 4])      ; i += 4

    dec["foc_sensor_mode"] = result.data[i]                         ; i += 1

    dec["foc_pll_kp"] = float32_from_bytes_auto(result.data[i: i + 4])          ; i += 4
    dec["foc_pll_ki"] = float32_from_bytes_auto(result.data[i: i + 4])          ; i += 4
    dec["foc_motor_l"] = float32_from_bytes_auto(result.data[i: i + 4])         ; i += 4
    dec["foc_motor_ld_lq_diff"] = float32_from_bytes_auto(result.data[i: i + 4])    ; i += 4
    dec["foc_motor_r"] = float32_from_bytes_auto(result.data[i: i + 4])         ; i += 4
    dec["foc_motor_flux_linkage"] = float32_from_bytes_auto(result.data[i: i + 4])      ; i += 4
    dec["foc_observer_gain"] = float32_from_bytes_auto(result.data[i: i + 4])       ; i += 4
    dec["foc_observer_gain_slow"] = float32_from_bytes_auto(result.data[i: i + 4])      ; i += 4
    dec["foc_duty_dowmramp_kp"] = float32_from_bytes_auto(result.data[i: i + 4])    ; i += 4
    dec["foc_duty_dowmramp_ki"] = float32_from_bytes_auto(result.data[i: i + 4])    ; i += 4
    dec["foc_openloop_rpm"] = float32_from_bytes_auto(result.data[i: i + 4])        ; i += 4

    dec["foc_openloop_rpm_low"] = float_from_bytes(result.data[i: i + 2], 1000)     ; i += 2

    dec["foc_d_gain_scale_start"] = float32_from_bytes_auto(result.data[i: i + 4])      ; i += 4
    dec["foc_d_gain_scale_max_mod"] = float32_from_bytes_auto(result.data[i: i + 4])    ; i += 4

    dec["foc_sl_openloop_hyst"] = float_from_bytes(result.data[i: i + 2], 100)      ; i += 2
    dec["foc_sl_openloop_time_lock"] = float_from_bytes(result.data[i: i + 2], 100)     ; i += 2
    dec["foc_sl_openloop_time_ramp"] = float_from_bytes(result.data[i: i + 2], 100)     ; i += 2
    dec["foc_sl_openloop_time"] = float_from_bytes(result.data[i: i + 2], 100)      ; i += 2

    dec["foc_hall_table"] = dict()
    dec["foc_hall_table"][0] = result.data[i]   ; i += 1
    dec["foc_hall_table"][1] = result.data[i]   ; i += 1
    dec["foc_hall_table"][2] = result.data[i]   ; i += 1
    dec["foc_hall_table"][3] = result.data[i]   ; i += 1
    dec["foc_hall_table"][4] = result.data[i]   ; i += 1
    dec["foc_hall_table"][5] = result.data[i]   ; i += 1
    dec["foc_hall_table"][6] = result.data[i]   ; i += 1
    dec["foc_hall_table"][7] = result.data[i]   ; i += 1

    # control point: ok decoding (checked)

    dec["foc_hall_interp_erpm"] = float32_from_bytes_auto(result.data[i: i + 4])    ; i += 4
    dec["foc_sl_erpm"] = float32_from_bytes_auto(result.data[i: i + 4])         ; i += 4

    dec["foc_sample_v0_v7"] = result.data[i]                        ; i += 1
    dec["foc_sample_high_current"] = result.data[i]                     ; i += 1

    dec["foc_sat_comp"] = float_from_bytes(result.data[i: i + 2], 1000)         ; i += 2
    dec["foc_temp_comp"] = result.data[i]                           ; i += 1
    dec["foc_temp_comp_base_temp"] = float_from_bytes(result.data[i: i + 2], 100)       ; i += 2
    dec["foc_current_filter_const"] = float32_from_bytes_auto(result.data[i: i + 4])    ; i += 4

    dec["foc_cc_decoupling"] = result.data[i]                       ; i += 1
    dec["foc_observer_type"] = result.data[i]                       ; i += 1

    dec["foc_hfi_voltage_start"] = float32_from_bytes_auto(result.data[i: i + 4])       ; i += 4
    dec["foc_hfi_voltage_run"] = float32_from_bytes_auto(result.data[i: i + 4])     ; i += 4
    dec["foc_hfi_voltage_max"] = float32_from_bytes_auto(result.data[i: i + 4])     ; i += 4
    dec["foc_sl_erpm_hfi"] = float32_from_bytes_auto(result.data[i: i + 4])         ; i += 4

    dec["foc_hfi_start_samples"] = uint_from_bytes(result.data[i: i + 2])           ; i += 2
    dec["foc_sl_erpm_hfi"] = float32_from_bytes_auto(result.data[i: i + 4])         ; i += 4
    dec["foc_hfi_samples"] = result.data[i]                         ; i += 1
    dec["gpd_buffer_notify_left"] = uint_from_bytes(result.data[i: i + 2])          ; i += 2
    dec["gpd_buffer_interpol"] = uint_from_bytes(result.data[i: i + 2])         ; i += 2

    dec["gpd_current_filter_const"] = float32_from_bytes_auto(result.data[i: i + 4])    ; i += 4
    dec["gpd_current_kp"] = float32_from_bytes_auto(result.data[i: i + 4])          ; i += 4
    dec["gpd_current_ki"] = float32_from_bytes_auto(result.data[i: i + 4])          ; i += 4
    dec["s_pid_kp"] = float32_from_bytes_auto(result.data[i: i + 4])            ; i += 4
    dec["s_pid_ki"] = float32_from_bytes_auto(result.data[i: i + 4])            ; i += 4
    dec["s_pid_kd"] = float32_from_bytes_auto(result.data[i: i + 4])            ; i += 4
    dec["s_pid_kd_filter"] = float32_from_bytes_auto(result.data[i: i + 4])         ; i += 4
    dec["s_pid_min_erpm"] = float32_from_bytes_auto(result.data[i: i + 4])          ; i += 4

    dec["s_pid_allow_braking"] = result.data[i]                     ; i += 1

    dec["s_pid_ramp_erpms_s"] = float32_from_bytes_auto(result.data[i: i + 4])      ; i += 4
    dec["p_pid_kp"] = float32_from_bytes_auto(result.data[i: i + 4])            ; i += 4
    dec["p_pid_ki"] = float32_from_bytes_auto(result.data[i: i + 4])            ; i += 4
    dec["p_pid_kd"] = float32_from_bytes_auto(result.data[i: i + 4])            ; i += 4
    dec["p_pid_kd_filter"] = float32_from_bytes_auto(result.data[i: i + 4])         ; i += 4
    dec["p_pid_ang_div"] = float32_from_bytes_auto(result.data[i: i + 4])           ; i += 4
    dec["cc_startup_boost_duty"] = float32_from_bytes_auto(result.data[i: i + 4])       ; i += 4
    dec["cc_min_current"] = float32_from_bytes_auto(result.data[i: i + 4])          ; i += 4
    dec["cc_gain"] = float32_from_bytes_auto(result.data[i: i + 4])             ; i += 4
    dec["cc_ramp_step_max"] = float32_from_bytes_auto(result.data[i: i + 4])        ; i += 4

    dec["m_fault_stop_time_ms"] = uint_from_bytes(result.data[i: i + 4])        ; i += 4

    # control point: ok decoding (checked)

    dec["m_duty_ramp_step"] = float32_from_bytes_auto(result.data[i: i + 4])        ; i += 4
    dec["m_current_backoff_gain"] = float32_from_bytes_auto(result.data[i: i + 4])      ; i += 4
    dec["m_encoder_counts"] = uint_from_bytes(result.data[i: i + 4])            ; i += 4

    dec["m_sensor_port_mode"] = result.data[i]                      ; i += 1
    dec["m_invert_direction"] = result.data[i]                      ; i += 1
    dec["m_drv8301_oc_mode"] = result.data[i]                       ; i += 1
    dec["m_drv8301_oc_adj"] = result.data[i]                        ; i += 1

    dec["m_bldc_f_sw_min"] = float32_from_bytes_auto(result.data[i: i + 4])         ; i += 4
    dec["m_bldc_f_sw_max"] = float32_from_bytes_auto(result.data[i: i + 4])         ; i += 4
    dec["m_dc_f_sw"] = float32_from_bytes_auto(result.data[i: i + 4])           ; i += 4
    dec["m_ntc_motor_beta"] = float32_from_bytes_auto(result.data[i: i + 4])        ; i += 4

    dec["m_out_aux_mode"] = result.data[i]                          ; i += 1
    dec["m_motor_temp_sens_type"] = result.data[i]                      ; i += 1

    dec["m_ptc_motor_coeff"] = float32_from_bytes_auto(result.data[i: i + 4])       ; i += 4

    dec["m_hall_extra_samples"] = result.data[i]                    ; i += 1
    dec["si_motor_poles"] = result.data[i]                          ; i += 1

    dec["si_gear_ratio"] = float32_from_bytes_auto(result.data[i: i + 4])           ; i += 4
    dec["si_wheel_diameter"] = float32_from_bytes_auto(result.data[i: i + 4])       ; i += 4
    dec["si_battery_type"] = result.data[i]                         ; i += 1
    dec["si_battery_cells"] = result.data[i]                        ; i += 1
    dec["si_battery_ah"] = float32_from_bytes_auto(result.data[i: i + 4])           ; i += 4

    # control point: ok decoding (checked)

    dec["bms"] = dict()
    dec["bms"]["type"] = result.data[i]                         ; i += 1
    dec["bms"]["t_limit_start"] = float_from_bytes(result.data[i: i + 2], 100)      ; i += 2
    dec["bms"]["t_limit_end"] = float_from_bytes(result.data[i: i + 2], 100)        ; i += 2
    dec["bms"]["soc_limit_start"] = float_from_bytes(result.data[i: i + 2], 1000)       ; i += 2
    dec["bms"]["soc_limit_end"] = float_from_bytes(result.data[i: i + 2], 1000)     ; i += 2

    return dec