import sys
if sys.version[0] == '3':
    from .DetectorManagerThread import DetectorManagerThread
from .FlatPanelEnums import ErrorCodes, Sort, Sequence, CommChannel, SyncMode, BoardType, \
    XisDetectorSupportOptions, BinningMode, TriggerMode, GbIFInitType, Gain_NOP_Series, Gain_16x0_AM, FunctionCode

