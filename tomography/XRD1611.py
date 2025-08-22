# -*- coding: utf-8 -*-
# python 2.7 #
import sys

if sys.version[0] != '2':
    raise SystemError("Python 3 is not supported.")

import numpy as np
import select
import traceback
from socket import socket, AF_INET, SOCK_STREAM

from flat_panel import *
from Socket import send_message, recv_unpack_message
from utils import get_perf_function_call, get_config

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
rows_ = rows
columns_ = columns
frames = 1
frames_in_sequence = 0
frame_number = 0
print("Creating empty arrays for data...")
np_frame_buffer = np.zeros((rows, columns), dtype=np.uint32)
processed_data = (c_ushort * rows * columns * frames)()


def bin_image(image, binning_mode, dtype=np.uint16):
    coef = 1 if binning_mode & BinningMode.B_1x1 else 2 if binning_mode & BinningMode.B_1x2 else 4
    if binning_mode & BinningMode.B_AVG:
        img = dtype(image.reshape(rows_, coef, columns_, coef).mean(axis=(1, 3)))
    elif binning_mode & BinningMode.B_SUM:
        img = dtype(image.reshape(rows_, coef, columns_, coef).sum(axis=(1, 3)))
    else:
        return None
    return img


ob_image = 0
ob_buffer = 0
df_image = 0
df_buffer = 0
bpm_image = 0
bpm_buffer = 0
corrections_loaded = False

def end_frame_callback_(_handle):
    global frame_number, np_frame_buffer, frames_in_sequence
    print("End of frame {} of {}".format(frame_number, frames_in_sequence))
    if frame_number >= frames_in_sequence:
        return
    frame_number += 1
    _ret = xis.Acquisition_GetAcqData(_handle, byref(processed_data))
    data = np.array(processed_data[0])
    np_frame_buffer += data
    send_message(sock, FunctionCode.end_frame_callback, _ret, data)


def end_acq_callback_(_handle):
    global frame_number, frames_in_sequence, np_frame_buffer
    print("End of sequence of {} frames".format(frames_in_sequence))
    sequence_result = np.uint16(np_frame_buffer // frames_in_sequence)
    _ret = ErrorCode.OK if frames_in_sequence == frame_number else ErrorCode.ACQUISITION
    send_message(sock, FunctionCode.end_acq_callback, _ret, sequence_result)
    np_frame_buffer[:] = 0


def acquire_image_local(handle, frames):
    if is_acquiring_data(handle):
        return ErrorCode.ACQ_ALREADY_RUNNING
    global frame_number, frames_in_sequence
    frames_in_sequence = frames
    frame_number = 0
    if corrections_loaded:
        return acquire_image_preloaded_corrections(handle, frames)
    else:
        return acquire_image(handle, frames)


def set_corr_image_local(handle, image, correction_type):
    ret, b_mode = get_camera_binning_mode(handle)
    if correction_type == "ob":
        global ob_image, ob_buffer, df_image
        if image == 0: return ErrorCode.OK
        ob_image = image
        ob_image_ = np.uint32(np.median(image) * 65536 / (image - df_image))
        ob_buffer = bin_image(ob_image_, b_mode, np.uint32).ctypes
        return ErrorCode.OK
    elif correction_type == "df":
        global df_image, df_buffer
        if image == 0: return ErrorCode.OK
        df_image = image
        df_buffer = bin_image(df_image, b_mode).ctypes
        return ErrorCode.OK
    elif correction_type == "bpm":
        global bpm_image, bpm_buffer
        if image == 0: return ErrorCode.OK
        if image.mean() == 0:
            bpm_image = 0
            bpm_buffer = 0
            return ErrorCode.OK
        bpm_image = image
        bpm_buffer = bin_image(bpm_image * np.iinfo(np.uint16).max, b_mode, np.uint32).ctypes
        ret, bpm_buffer, corr_list_size = create_pixel_map(bpm_buffer, rows_, columns_)
        return ret
    else:
        return ErrorCode.ACQUISITION


def set_camera_binning_mode_local(handle, binning_mode):
    global columns_, rows_, ob_buffer, df_buffer, bpm_buffer
    ret = set_camera_binning_mode(handle, binning_mode)
    if ret != ErrorCode.OK:
        return ret
    coef = 1 if binning_mode & BinningMode.B_1x1 else 2 if binning_mode & BinningMode.B_1x2 else 4
    columns_ = columns // coef
    rows_ = rows // coef
    if set_corr_image_local(handle, ob_image, "ob") != ErrorCode.OK:
        return ErrorCode.ACQ
    if set_corr_image_local(handle, df_image, "df") != ErrorCode.OK:
        return ErrorCode.ACQ
    if set_corr_image_local(handle, bpm_image, "bpm") != ErrorCode.OK:
        return ErrorCode.ACQ
    return ErrorCode.OK


# TODO: Solve correction images - have to be send from GUI, rotation and mirror set in here
# TODO: Remove preview from detector widget -> tomography widget itself


CALLBACK_TYPE = CFUNCTYPE(None, c_void_p)
c_end_frame_cb = CALLBACK_TYPE(end_frame_callback_)
c_end_data_cb = CALLBACK_TYPE(end_acq_callback_)

perform_function_call(sock, set_callbacks_and_messages, handle, c_end_frame_cb, c_end_data_cb, failure=True, response = "args")
perform_function_call(sock, define_dest_buffers, handle, processed_data, frames, rows, columns, response = "args")
perform_function_call(sock, set_camera_binning_mode, handle, BinningMode.B_AVG | BinningMode.B_1x1, response = "args")
perform_function_call(sock, set_camera_trigger_mode, handle, TriggerMode.TriggerFrames, response = "args")
perform_function_call(sock, set_camera_gain, handle, Gain_NOP_Series.g_0p25, response = "args")
perform_function_call(sock, set_camera_mode, handle, 0, response = "args")  # the base time will be timing 0
perform_function_call(sock, set_frame_sync_mode, handle, SyncMode.INTERNAL_TIMER, response = "args")
perform_function_call(sock, set_timer_sync, handle, 1000000, response = "args")  # sets the timer to 1 s

while True:
    try:
        ready_to_read, _, _ = select.select([sock], [], [], float(config["timeout"]))
        if ready_to_read:
            try:
                func_code, status_code, message = recv_unpack_message(sock)
                if message[0] is None:
                    message = []
                local_fn_name = "{}_local".format(FunctionCode.name(func_code))
                fn = globals()[local_fn_name] if local_fn_name in globals() else globals()[FunctionCode.name(func_code)]
                perform_function_call(sock, fn, handle, *message)
            except Exception as e:
                print("Cannot unpack message:", e)
                print(traceback.format_exc())
                break
    except KeyboardInterrupt:
        break

print("Closing detector connection...")
close(handle)
print("Closing socket...")
sock.close()
print("Closed gracefully.")
