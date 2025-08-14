# -*- coding: utf-8 -*-
# python 2.7 #
import sys
if sys.version[0] != '2':
    raise SystemError("Python 3 is not supported.")

import numpy as np
import select
from socket import socket, AF_INET, SOCK_STREAM

from flat_panel import *
from Socket import send_message, recv_unpack_message
from utils import get_perf_function_call, get_config, ctypes_array_type_convert

config = dict(get_config().items("Server"))
sock = socket(AF_INET, SOCK_STREAM)
perform_function_call = get_perf_function_call(ErrorCode, FunctionCode, 0, send_message)

try:
    print("Connecting to server at {}:{}".format(config["host"], config["port"]))
    sock.connect((config["host"], int(config["port"])))
except Exception as e:
    print("Cannot connect to server:", e)
    exit(1)

##### init_detector #####
send_message(sock, FunctionCode.server_connect, 0, "XRD1611")
print("Initializing detector...")
number = perform_function_call(sock, enum_sensors, failure=True)
print("Detected {} sensors. Using only the first one...".format(number))
pos, handle = perform_function_call(sock, get_next_sensor, failure=True)

(frames, rows, columns, sort_flags, irq_enabled, sync_mode) = perform_function_call(sock, get_configuration, handle,
                                                                                    failure=True)
frames = 1
print("Creating empty arrays for data...")
processed_data = (c_ushort * rows * columns * frames)()
ob_buffer = (c_ushort * rows * columns)()
df_buffer = (c_ushort * rows * columns)()
bpm_buffer = (c_ushort * rows * columns)()


def end_frame_callback_(_handle):
    print("End of frame")
    _ret = xis.Acquisition_GetAcqData(_handle, byref(processed_data))
    data = np.array(processed_data[0])
    send_message(sock, FunctionCode.end_frame_callback, _ret, data)


def end_acq_callback_(_handle):
    print("End of sequence.")
    send_message(sock, FunctionCode.end_acq_callback, 0, "")


CALLBACK_TYPE = CFUNCTYPE(None, c_void_p)
c_end_frame_cb = CALLBACK_TYPE(end_frame_callback_)
c_end_data_cb = CALLBACK_TYPE(end_acq_callback_)

perform_function_call(sock, set_callbacks_and_messages, handle, c_end_frame_cb, c_end_data_cb, failure=True)
perform_function_call(sock, define_dest_buffers, handle, processed_data, frames, rows, columns)
perform_function_call(sock, set_camera_binning_mode, handle, BinningMode.B_AVG | BinningMode.B_1x1)
perform_function_call(sock, set_camera_trigger_mode, handle, TriggerMode.TriggerFrames)
perform_function_call(sock, set_camera_gain, handle, Gain_NOP_Series.g_0p25)
perform_function_call(sock, set_camera_mode, handle, 0)  # the base time will be timing 0
perform_function_call(sock, set_frame_sync_mode, handle, SyncMode.INTERNAL_TIMER)
perform_function_call(sock, set_timer_sync, handle, 1000000)  # sets the timer to 1 s


while True:
    try:
        ready_to_read, _, _ = select.select([sock], [], [], float(config["timeout"]))
        if ready_to_read:
            try:
                func_code, status_code, message = recv_unpack_message(sock)
                if message[0] is None:
                    message = []
                perform_function_call(sock, globals()[FunctionCode.name(func_code)], handle, *message)
            except Exception as e:
                print("Cannot unpack message:", e)
                break
    except KeyboardInterrupt:
        break

print("Closing detector connection...")
close(handle)
print("Closing socket...")
sock.close()
print("Closed gracefully.")
