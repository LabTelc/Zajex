# -*- coding: utf-8 -*-
"""
@author: Vopalensky
@author: Zajicek
"""
# python 2.7 #
import sys

if sys.version[0] != '2':
    raise SystemError("Python 3 is not supported.")


class ErrorCodes:
    """
    Error codes for the XIS library.
    """
    ALL_OK = 0
    MEMORY = 1
    BOARDINIT = 2
    NOCAMERA = 3
    CORRBUFFER_INCOMPATIBLE = 4
    ACQ_ALREADY_RUNNING = 5
    TIMEOUT = 6
    INVALIDACQDESC = 7
    VXDNOTFOUND = 8
    VXDNOTOPEN = 9
    VXDUNKNOWNERROR = 10
    VXDGETDMAADR = 11
    ACQABORT = 12
    ACQUISITION = 13
    VXD_REGISTER_IRQ = 14
    VXD_REGISTER_STATADR = 15
    GETOSVERSION = 16
    SETFRMSYNC = 17
    SETFRMSYNCMODE = 18
    SETTIMERSYNC = 19
    INVALID_FUNC_CALL = 20
    ABORTCURRFRAME = 21
    GETHWHEADERINFO = 22
    HWHEADER_INV = 23
    SETLINETRIG_MODE = 24
    WRITE_DATA = 25
    READ_DATA = 26
    SETBAUDRATE = 27
    NODESC_AVAILABLE = 28
    BUFFERSPACE_NOT_SUFF = 29
    SETCAMERAMODE = 30
    FRAME_INV = 31
    SLOW_SYSTEM = 32
    GET_NUM_BOARDS = 33
    HW_ALREADY_OPEN_BY_ANOTHER_PROCESS = 34
    CREATE_MEMORYMAPPING = 35
    VXD_REGISTER_DMA_ADDRESS = 36
    VXD_REGISTER_STAT_ADDR = 37
    VXD_UNMASK_IRQ = 38
    LOADDRIVER = 39
    FUNC_NOTIMPL = 40
    MEMORY_MAPPING = 41
    CREATE_MUTEX = 42
    ACQ = 43
    DESC_NOT_LOCAL = 44
    INVALID_PARAM = 45
    ABORT = 46
    WRONGBOARDSELECT = 47
    WRONG_CAMERA_MODE = 48
    AVERAGED_LOST = 49
    BAD_SORTING_PARAM = 50
    UNKNOWN_IP_MAC_NAME = 51
    NO_BOARD_IN_SUBNET = 52
    UNABLE_TO_OPEN_BOARD = 53
    UNABLE_TO_CLOSE_BOARD = 54
    UNABLE_TO_ACCESS_DETECTOR_FLASH = 55
    HEADER_TIMEOUT = 56
    NO_PING_ACK = 57
    NR_OF_BOARDS_CHANGED = 58

    _reverse_dict = None

    @classmethod
    def _build_reverse_dict(cls):
        if not cls._reverse_dict:
            cls._reverse_dict = {
                getattr(cls, attr): attr
                for attr in dir(cls)
                if attr.isupper()
            }

    @staticmethod
    def name(value):
        ErrorCodes._build_reverse_dict()
        return ErrorCodes._reverse_dict.get(value, "UNKNOWN")


class Sort:
    """
    Sorting definitions for the XIS library.
    """
    NOSORT = 0
    QUAD = 1
    COLUMN = 2
    COLUMNQUAD = 3
    QUAD_INVERSE = 4
    QUAD_TILE = 5
    QUAD_TILE_INVERSE = 6
    QUAD_TILE_INVERSE_SCRAMBLE = 7
    OCT_TILE_INVERSE = 8  # 1640 and 1620
    OCT_TILE_INVERSE_BINDING = 9  # 1680
    OCT_TILE_INVERSE_DOUBLE = 10  # 1620 reverse
    HEX_TILE_INVERSE = 11  # 1621 ADIC
    HEX_CS = 12  # 1620/1640 continous scan
    sort_12x1 = 13  # 12X1 Combo
    sort_14 = 14  #


# sequence acquisition options
class Sequence:
    """
        Sorting definitions for the XIS library.
        """
    TWO_BUFFERS = 0x1
    ONE_BUFFER = 0x2
    AVERAGE = 0x4
    DEST_ONE_FRAME = 0x8
    COLLATE = 0x10
    CONTINUOUS = 0x100
    LEAKAGE = 0x1000
    NONLINEAR = 0x2000
    AVERAGESEQ = 0x4000  # sequence of averaged frames


class SyncMode:
    """
    Synchronization modes for the XIS library.
    """
    SOFT_TRIGGER = 1
    INTERNAL_TIMER = 2
    EXTERNAL_TRIGGER = 3
    FREE_RUNNING = 4


class CameraMode:
    """
    Camera modes for the XIS library.
    """
    SETSYNC = 0x8
    TIMEMASK = 0x7
    FPGA = 0x7F


class BoardType:
    NOONE = 0x0
    ELTEC = 0x1
    DIPIX = 0x2
    RS232 = 0x3
    USB = 0x4
    # ELTEC_SCIURIUS	=		0x8
    ELTEC_XRD_FGX = 0x8
    ELTEC_XRD_FGE_Opto = 0x10
    ELTEC_GbIF = 0x20


class XisDetectorSupportOptions:
    """
    Detector supported options for the XIS library.
    """
    SERVICE_MODE_AVAILABLE = 0x1
    TRIGGER_SOURCE_SELECTABLE = 0x2
    SUPPORTS_PING = 0x3
    SUPPORTED_ROI_MODES = 0x4
    SUPPORTED_BINNING_MODES = 0x5
    SUPPORTS_GAIN_CHANGE = 0x6
    SUPPORTS_MULTIPLE_TRIGGER_MODES = 0x7
    SUPPORTS_CONFIGURABLE_TRIGGER_OUT = 0x8
    GRPSIZE_ROI_Y = 0x9
    LIVEBUFFERSIZE = 0xA


class BinningMode:
    """
    Binning modes for the XIS library.
    """
    B_1x1 = 0x1
    B_2x2 = 0x2
    B_4x4 = 0x4
    B_1x2 = 0x8
    B_1x4 = 0x10

    B_AVG = 0x100
    B_SUM = 0x200

class TriggerMode:
    """
    Trigger modes for the XIS library.
    """
    DDD_WM = 0 # WM/DDD
    DDD_WM_no_clearance_scan = 1 # WM/DDD without clearance scan
    StartStop = 2 # Start Stop
    TriggerFrames = 3 # Trigger frames (trigger first type)
    AutoTriggerFrames = 4 # AutoTrigger frames
    TriggerOnRowTag = 5 #  Trigger on row tag (framewise with filter on trigger input) / RnF frameWise flow controlled
    SingleShot = 6 # Single shot with post offset by single trigger (second trigger aborts readout of bright image)- XRPAD2 only
    DualEnergy = 7 # Dual energy with post offset- XRPAD2 only

class GbIFInitType:
    """
    To identify of which type the parameter cAddress
    """
    IP = 1
    MAC = 2
    NAME = 3


class Gain_16x0_AM:
    """
    Gain settings for the 16x0 AM series detectors, in Farads.
    """
    g_0p1 = 0
    g_0p3 = 1
    g_0p9 = 2
    g_4p7 = 4
    g_10p = 8


class Gain_NOP_Series:
    """
    Gain settings for the xN/xO/xP series detectors, in Farads.
    """
    g_0p25 = 0
    g_0p5 = 1
    g_1p = 2
    g_2p = 3
    g_4p = 4
    g_8p = 5
