# -*- coding: utf-8 -*-
"""
@author: Vopalensky
@author: Zajicek
"""
# python 2.7 #
import sys

if sys.version[0] != '2':
    raise SystemError("Python 3 is not supported.")


import os.path
dllPath = os.path.dirname(__file__)
dllPath = os.path.join(dllPath, 'XISL.dll')

from ctypes import *

xis = CDLL(dllPath)

DWORD = c_ulong
BOOL = c_bool
GBIF_STRING_DATATYPE = c_char
CHAR = c_char
WORD = c_ushort
UCHAR = c_ubyte
FLOAT = c_float
DOUBLE = c_double
UINT = c_uint

HACQDESC = c_void_p

GBIF_IP_MAC_NAME_CHAR_ARRAY_LENGTH = 16

HIS_GbIF_FIRST_CAM = 0

HIS_GbIF_IP_STATIC = 1
HIS_GbIF_IP_DHCP = 2
HIS_GbIF_IP_LLA = 4

HIS_MAX_TIMINGS = 0x8