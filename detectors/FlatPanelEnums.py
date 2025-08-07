# -*- coding: utf-8 -*-
"""
@author: Vopalensky
@author: Zajicek
"""


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


class CommChannel:
    NONE = 0x00
    ELTEC_XRD_FGe = 0x01
    ELTEC_XRD_FGX = 0x08
    ELTEC_XRD_FGE_Opto = 0x10
    ELTEC_GbIF = 0x20
    ELTEC_EMBEDDED = 0x60

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
        CommChannel._build_reverse_dict()
        return CommChannel._reverse_dict.get(value, "UNKNOWN")


class SyncMode:
    """
    Synchronization modes for the XIS library.
    """
    SOFT_TRIGGER = 1
    INTERNAL_TIMER = 2
    EXTERNAL_TRIGGER = 3
    FREE_RUNNING = 4


# class CameraMode:
#     """
#     Camera modes for the XIS library.
#     """
#     SETSYNC = 0x8
#     TIMEMASK = 0x7
#     FPGA = 0x7F


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
    DDD_WM = 0  # WM/DDD
    DDD_WM_no_clearance_scan = 1  # WM/DDD without clearance scan
    StartStop = 2  # Start Stop
    TriggerFrames = 3  # Trigger frames (trigger first type)
    AutoTriggerFrames = 4  # AutoTrigger frames
    TriggerOnRowTag = 5  # Trigger on row tag (framewise with filter on trigger input) / RnF frameWise flow controlled
    SingleShot = 6  # Single shot with post offset by single trigger (second trigger aborts readout of bright image)- XRPAD2 only
    DualEnergy = 7  # Dual energy with post offset- XRPAD2 only


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


class FunctionCode:
    gb_if_get_device_count = 0
    gb_if_get_device_list = 1
    gb_if_init = 2
    gb_if_get_device = 3
    gb_if_get_device_params = 4
    gb_if_set_connection_settings = 5
    gb_if_get_connection_settings = 6
    gb_if_force_ip = 7
    gb_if_set_packet_delay = 8
    gb_if_get_packet_delay = 9
    gb_if_check_network_speed = 10
    gb_if_get_detector_properties = 11
    gb_if_get_filter_drv_state = 12
    get_configuration = 13
    get_hw_header_info = 14
    define_dest_buffers = 15
    acquire_offset_image = 16
    create_pixel_map = 17
    acquire_image = 18
    set_camera_mode = 19
    set_camera_gain = 20
    set_camera_binning_mode = 21
    get_camera_binning_mode = 22
    set_camera_trigger_mode = 23
    get_camera_trigger_mode = 24
    set_callbacks_and_messages = 25
    get_ready = 26
    set_ready = 27
    is_acquiring_data = 28
    get_acq_data = 29
    get_act_frame = 30
    close = 31
    close_all = 32
    abort = 33
    set_timer_sync = 34
    set_frame_sync_mode = 35
    enum_sensors = 36
    get_next_sensor = 37
    init = 38
    get_error_code = 39

    _reverse_dict = None

    @classmethod
    def _build_reverse_dict(cls):
        if not cls._reverse_dict:
            cls._reverse_dict = {getattr(cls, attr): attr for attr in dir(cls) if isinstance(attr, dict)}

    @staticmethod
    def name(value):
        FunctionCode._build_reverse_dict()
        return FunctionCode._reverse_dict.get(value, "UNKNOWN")


class ErrorCodes:
    """
    Error codes for the XIS library.
    """
    OK = 0
    ABORT = 46
    ABORTCURRFRAME = 21
    ACKNOWLEDGE_IMAGE = 133
    ACQ = 43
    ACQ_ALREADY_RUNNING = 5
    ACQABORT = 12
    ACQUISITION = 13
    ALREADY_EXISTS = 74
    AVERAGED_LOST = 49
    BAD_SORTING_PARAM = 50
    BOARDINIT = 2
    BUFFERSPACE_NOT_SUFF = 29
    CONFLICT = 167
    CORRBUFFER_INCOMPATIBLE = 4
    CREATE_MEMORYMAPPING = 35
    CREATE_MUTEX = 42
    CURL = 65
    DESC_NOT_LOCAL = 44
    DOES_NOT_EXIST = 75
    EMI_NOT_SET = 115
    ENABLE_INTERRUPTS = 108
    ENABLE_ONBOARD_GAINOFFSET = 68
    ENABLE_ONBOARD_MEAN = 67
    ENABLE_ONBOARD_OFFSET = 66
    ENABLE_ONBOARD_PREVIEW = 69
    FRAME_INV = 31
    FUNC_NOTIMPL = 40
    GET_AVAILABLE_SYSTEMS = 154
    GET_CHARGE_MODE = 139
    GET_NUM_BOARDS = 33
    GET_ONBOARD_OFFSET = 64
    GETHWHEADERINFO = 22
    GETOSVERSION = 16
    HEADER_TIMEOUT = 56
    HW_ALREADY_OPEN_BY_ANOTHER_PROCESS = 34
    HW_BOARD_CHANNEL_ALREADY_USED = 146
    HWHEADER_INV = 23
    ILLEGAL_INDEX = 60
    INIT_DET_OPTIONS = 176
    INVALID_FILENAME = 77
    INVALID_FUNC_CALL = 20
    INVALID_HANDLE = 73
    INVALID_PARAM = 45
    INVALIDACQDESC = 7
    INVALIDBUFFERNR = 72
    LOAD_COORECTIONIMAGETOBUFFER = 71
    LOADDRIVER = 39
    MEMORY = 1
    MEMORY_MAPPING = 41
    MISSING_VERSION_INFORMATION = 143
    NO_BOARD_IN_SUBNET = 52
    NO_FPGA_ACK = 57
    NOCAMERA = 3
    NODESC_AVAILABLE = 28
    NOT_DISCOVERED = 62
    NOT_INITIALIZED = 61
    NOT_SUPPORTED = 165
    NR_OF_BOARDS_CHANGED = 58
    ONBOARDAVGFAILED = 63
    OPEN_FILE = 76
    READ_DATA = 26
    RESET_ZYNQ = 172
    RETRIEVE_ENHANCED_HEADER = 107
    SET_CHARGE_MODE = 118
    SET_EVENT_CALLBACK = 169
    SET_IDLE_TIMEOUT = 117
    SET_IMAGE_TAG = 104
    SET_IMAGE_TAG_LENGTH = 106
    SET_ONBOARD_BINNING = 70
    SET_PACKET_DELAY = 153
    SET_PROC_SCRIPT = 105
    SETBAUDRATE = 27
    SETCAMERAMODE = 30
    SETDISCOVERYTIMEOUT = 78
    SETEXAMFLAG = 59
    SETFRMSYNC = 17
    SETFRMSYNCMODE = 18
    SETHEADERSIZE = 160
    SETLINETRIG_MODE = 24
    SETREGISTERTIMEOUT = 161
    SETTIMERSYNC = 19
    SLOW_SYSTEM = 32
    TIMEOUT = 6
    TRANSMISSION_MODE = 166
    UNABLE_TO_ACCESS_DETECTOR_FLASH = 55
    UNABLE_TO_CLOSE_BOARD = 54
    UNABLE_TO_OPEN_BOARD = 53
    UNKNOWN_IP_MAC_NAME = 51
    VXD_REGISTER_DMA_ADDRESS = 36
    VXD_REGISTER_IRQ = 14
    VXD_REGISTER_STAT_ADDR = 37
    VXD_REGISTER_STATADR = 15
    VXD_UNMASK_IRQ = 38
    VXDGETDMAADR = 11
    VXDNOTFOUND = 8
    VXDNOTOPEN = 9
    VXDUNKNOWNERROR = 10
    WLAN_RESTART = 168
    WRITE_DATA = 25
    WRONG_CAMERA_MODE = 48
    WRONGBOARDSELECT = 47
    WSA = 164
    XRPD_BATTERY_COM = 163
    XRPD_CONNECT = 134
    XRPD_CREATE_FAKE_SHOCK_EVENT = 112
    XRPD_CREATE_FAKE_SHOCK_EVENT_CRIT = 119
    XRPD_CREATE_FAKE_SHOCK_EVENT_WARN = 120
    XRPD_DETECTOR_IN_DEEP_SLEEP = 157
    XRPD_DISABLE_SYSLOG_SAVING = 152
    XRPD_FACTORY_RESET_SHOCK_EVENT = 121
    XRPD_GET_AUTOPOWERONLOCATIONS = 137
    XRPD_GET_CURRENT_VOLTAGE = 147
    XRPD_GET_DEEPSLEEPIDLELOCATIONS = 155
    XRPD_GET_DEF_BOOT_CFG = 170
    XRPD_GET_DET_OPTIONS = 175
    XRPD_GET_DET_TYPE = 174
    XRPD_GET_EPC_REGISTER = 159
    XRPD_GET_SDCARD_INFO = 113
    XRPD_GET_SDCARD_TIMEOUT = 142
    XRPD_GET_TEMP_VALUES = 158
    XRPD_GET_TEMPERATURE_THRESHOLDS = 129
    XRPD_GET_WLAN_CC = 149
    XRPD_GET_WLAN_ChannelList = 151
    XRPD_NO_EVENT_INTERFACE = 111
    XRPD_NO_EVENTCALLBACK_DEFINED = 130
    XRPD_NO_LOCATION = 116
    XRPD_NO_NETWORK = 122
    XRPD_NOT_CONNECTED = 144
    XRPD_REQUEST_POWERSTATE = 136
    XRPD_RESEND_ALL_MSG = 132
    XRPD_RESET_SHOCK = 135
    XRPD_RESET_TEMPERATURE_TIMEOUT = 127
    XRPD_SDCARDPERFORMANCE = 145
    XRPD_SESSION_ERROR = 109
    XRPD_SET_AUTOPOWERONLOCATIONS = 138
    XRPD_SET_CPUFREQ_GOVERNOR = 148
    XRPD_SET_DATE_TIME = 131
    XRPD_SET_DEEPSLEEPIDLELOCATIONS = 156
    XRPD_SET_DEF_BOOT_CFG = 171
    XRPD_SET_EPC_REGISTER = 162
    XRPD_SET_EVENT = 110
    XRPD_SET_FORCE_FSCK = 140
    XRPD_SET_NETWORK = 123
    XRPD_SET_PRIVATE_KEY = 125
    XRPD_SET_SDCARD_TIMEOUT = 141
    XRPD_SET_TEMP_FAKE_MODE = 114
    XRPD_SET_TEMPERATURE_THRESHOLDS = 128
    XRPD_SET_TEMPERATURE_TIMEOUT = 126
    XRPD_SET_WLAN_CC = 150
    XRPD_VERIFY_GENUINENESS = 124

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
