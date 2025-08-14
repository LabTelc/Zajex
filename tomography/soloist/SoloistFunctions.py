# -*- coding: utf-8 -*-
"""
Created on Mon Sep 04 13:20:28 2017

@author: Michal Vopalensky
@author: Antonin Zajicek
"""
# python 2.7 #
import sys

from SoloistEnums import StatusItem

if sys.version[0] != '2':
    raise SystemError("Python 3 is not supported.")

import os
from ctypes import *

dllpath = os.path.dirname(__file__)
ablib = CDLL(os.path.join(dllpath, 'AeroBasic64.dll'))
corelib = CDLL(os.path.join(dllpath, 'SoloistCore64.dll'))
sclib = CDLL(os.path.join(dllpath, 'SoloistC64.dll'))

SoloistHandle = c_void_p


# from SoloistConnection.h

def connect():
    """
    Connects the present Soloist devices.

    Connect()

    Returns (ret, handles, handle_count)
    ret = 1 in case of success
    handles - array of pointers to SoloistHandle objects
    handleCount - unsigned long number of found devices

    The individual handle is then extracted as handle = handles[0], handles[1] etc.
    """
    handles = pointer(SoloistHandle())
    handle_count = c_ulong()
    ret = sclib.SoloistConnect(byref(handles), byref(handle_count))
    return ret, handles, handle_count


def disconnect(handles):
    """
    Disconnects the Soloist devices specified in handles structure.

    Disconnect(handles)

    For handles see the help to Connect() function

    Returns 1 in case of success
    """
    return sclib.SoloistDisconnect(handles)


def reset(handle, restart_programs=False):
    """
    Resets the Soloist system.

    Reset(handle, restartPrograms = False)

    handle - handle to the Soloist device
    restartPrograms - True to run program automation after reset. (Not understood well from the original documentation.)

    Returns 1 on success, 0 on error.
    """
    return sclib.SoloistReset(handle, restart_programs)


def abort(handle):
    return sclib.SoloistAbort(handle)


# from SoloistAeroBasicCommands.h


def enable(handle):
    """
    Enables movement of the device specified in handle.

    Enable(handle)

    Returns 1 on success, 0 on error.
    """
    return sclib.SoloistMotionEnable(handle)


def disable(handle):
    return sclib.SoloistMotionDisable(handle)


def free_run(handle, speed):
    return sclib.SoloistMotionFreeRun(handle, c_double(speed))


def free_run_stop(handle):
    return sclib.SoloistMotionFreeRunStop(handle)


def home(handle):
    return sclib.SoloistMotionHome(handle)


def acknowledge_all(handle):
    """
    Acknowledges all axis faults and clears all task errors.
    """
    return sclib.SoloistAcknowledgeAll(handle)


def move(handle, distance, speed, absolute=False):
    if absolute:
        return sclib.SoloistMotionMoveAbs(handle, c_double(distance), c_double(speed))
    else:
        return sclib.SoloistMotionMoveInc(handle, c_double(distance), c_double(speed))


def wait_mode(handle, wait_type):
    """
    Represents the wait mode in AeroBasic
    Can be found in Enum WaitType
    """
    return sclib.SoloistMotionWaitMode(handle, wait_type)


def get_status_item(handle, item):
    """
    Gets the status item specified by StatusItem enum from the Soloist device specified by handle.
    """
    value = c_double()
    ret = sclib.SoloistStatusGetItem(handle, item, byref(value))
    return ret, value.value


def get_axis_status(handle):
    """
    Gets status from set {Homed, Enabled} of the specified axis.
    """
    ret, value = get_status_item(handle, StatusItem.AxisStatus)
    return ret, value


def get_program_position_feedback(handle):
    """
    Gets the program position feedback from the Soloist device specified by handle.
    """
    ret, value = get_status_item(handle, StatusItem.ProgramPositionFeedback)
    return ret, float(value)
