# -*- coding: utf-8 -*-
"""
@author: Vopalensky
@author: Zajicek
"""
# python 2.7 #
import sys

if sys.version[0] != '2':
    raise SystemError("Python 3 is not supported.")

from FlatPanelCommon import *

class GbifDeviceParam(Structure):
    _fields_ = [
        ("ucMacAddress", GBIF_STRING_DATATYPE * GBIF_IP_MAC_NAME_CHAR_ARRAY_LENGTH),
        ("ucIP", GBIF_STRING_DATATYPE * GBIF_IP_MAC_NAME_CHAR_ARRAY_LENGTH),
        ("ucSubnetMask", GBIF_STRING_DATATYPE * GBIF_IP_MAC_NAME_CHAR_ARRAY_LENGTH),
        ("ucGateway", GBIF_STRING_DATATYPE * GBIF_IP_MAC_NAME_CHAR_ARRAY_LENGTH),
        ("ucAdapterIP", GBIF_STRING_DATATYPE * GBIF_IP_MAC_NAME_CHAR_ARRAY_LENGTH),
        ("ucAdapterMask", GBIF_STRING_DATATYPE * GBIF_IP_MAC_NAME_CHAR_ARRAY_LENGTH),
        ("dwIPCurrentBootOptions", DWORD),
        ("cManufacturerName", CHAR * 32),
        ("cModelName", CHAR * 32),
        ("cGBIFFirmwareVersion", CHAR * 32),
        ("cDeviceName", CHAR * GBIF_IP_MAC_NAME_CHAR_ARRAY_LENGTH)
    ]


# using:
# c = pyGBIF_DEVICE_PARAM()
# dll.pyGetDeviceList(byref(c),2)
# c.ucIP
# or if the structure uses c_ubyte instead of c_char, to recover the values, as they are ascii coded
# [chr(x) for x in c.ucIP]


# usage with array of structs in the C function, as in pyGetDeviceList:
# c = (pyGBIF_DEVICE_PARAM * 2)() - instance of an array of two structs
# dll.pyGetDeviceList(byref(c), 2)
# c[0].ucIP
# c[1].ucIP


class CHwHeaderInfo(Structure):
    _fields_ = [
        ("dwPROMID", DWORD),
        ("dwHeaderID", DWORD),
        ("bAddRow", BOOL),
        ("bPwrSave", BOOL),
        ("dwNrRows", DWORD),
        ("dwNrColumns", DWORD),
        ("dwZoomULRow", DWORD),
        ("dwZoomULColumn", DWORD),
        ("dwZoomBRRow", DWORD),
        ("dwZoomBRColumn", DWORD),
        ("dwFrmNrRows", DWORD),
        ("dwFrmRowType", DWORD),
        ("dwFrmFillRowIntervalls", DWORD),
        ("dwNrOfFillingRows", DWORD),
        ("dwDataType", DWORD),
        ("dwDataSorting", DWORD),
        ("dwTiming", DWORD),
        ("dwAcqMode", DWORD),
        ("dwGain", DWORD),
        ("dwOffset", DWORD),
        ("dwAccess", DWORD),
        ("bSyncMode", BOOL),
        ("dwBias", DWORD),
        ("dwLeakRows", DWORD),
    ]


class GbifDetectorProperties(Structure):
    _fields_ = [
        ("cDetectorType", CHAR * 32),
        ("cManufacturingDate", CHAR * 8),
        ("cPlaceOfManufacture", CHAR * 8),
        ("cDummy", CHAR * 80)
    ]