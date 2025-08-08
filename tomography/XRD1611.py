# -*- coding: utf-8 -*-
# python 2.7 #
import sys
if sys.version[0] != '2':
    raise SystemError("Python 3 is not supported.")

import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
import select
from socket import socket, AF_INET, SOCK_STREAM

from flat_panel import *
from Socket import *

from utils import get_config

config = get_config()["Server"]

sock = socket(AF_INET, SOCK_STREAM)
try:
    print("Connecting to server at {}:{}".format(config["host"], config["port"]))
    sock.connect((config["host"], int(config["port"])))
except Exception as e:
    print("Cannot connect to server:", e)
    exit(1)

##### init_detector #####
print("Initializing detector...")
number = perform_function_call(sock, enum_sensors, failure=True, name="XRD1611")
print("Detected {} sensors. Using only the first one...".format(number))
pos, handle = perform_function_call(sock, get_next_sensor, failure=True)

(frames, rows, columns, sort_flags, irq_enabled, sync_mode) = perform_function_call(sock, get_configuration, handle,
                                                                                    failure=True)
frames = 1
temp_array = ()
print("Creating empty array for data...")
processed_data = (c_ushort * rows * columns * frames)()


def end_frame_callback(_handle):
    print("End of frame")
    _ret = xis.Acquisition_GetAcqData(_handle, byref(processed_data))
    data = np.array(processed_data[0])
    send_message(sock, FunctionCode.acquire_image, _ret, data)


def end_data_callback(_handle):
    print("End of data")
    _ret = xis.Acquisition_GetAcqData(_handle, byref(processed_data))
    data = np.array(processed_data[0])
    send_message(sock, FunctionCode.acquire_image, _ret, data)


CALLBACK_TYPE = CFUNCTYPE(None, c_void_p)
c_end_frame_cb = CALLBACK_TYPE(end_frame_callback)
c_end_data_cb = CALLBACK_TYPE(end_data_callback)

perform_function_call(sock, set_callbacks_and_messages, handle, c_end_frame_cb, c_end_data_cb, failure=True)
perform_function_call(sock, define_dest_buffers, handle, processed_data, frames, rows, columns)
perform_function_call(sock, set_camera_binning_mode, handle, BinningMode.B_AVG | BinningMode.B_1x1)
perform_function_call(sock, set_camera_trigger_mode, handle, TriggerMode.TriggerFrames)
perform_function_call(sock, set_camera_gain, handle, Gain_NOP_Series.g_0p25)
perform_function_call(sock, set_camera_mode, handle, 0)  # the base time will be timing 0
perform_function_call(sock, set_frame_sync_mode, handle, SyncMode.INTERNAL_TIMER)
perform_function_call(sock, set_timer_sync, handle, 1000000)  # sets the timer to 1 s
send_message(sock, FunctionCode.init, 0, "")

# for i in range(10):
#     perform_function_call(sock, acquire_image, handle, 1, 0, Sequence.DEST_ONE_FRAME)

while True:
    try:
        ready_to_read, _, _ = select.select([sock], [], [], float(config["timeout"]))
        if ready_to_read:
            try:
                func_code, status_code, message = recv_unpack_message(sock)
                perform_function_call(sock, FunctionCode.name(func_code), message.split(" "))
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
