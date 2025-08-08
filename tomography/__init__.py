import sys
if sys.version[0] == '3':
    from tomography.TomographyManagerThread import DetectorManagerThread
    from .ui_elements_classes import DetectorManagerWidget
    from .ui_elements_classes import XRD1611Widget
from tomography.flat_panel.FlatPanelEnums import ErrorCodes, Sort, Sequence, CommChannel, SyncMode, BoardType, \
    XisDetectorSupportOptions, BinningMode, TriggerMode, GbIFInitType, Gain_NOP_Series, Gain_16x0_AM, FunctionCode

