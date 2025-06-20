__all__ = ['BatchDialog', 'ClickHoldComboBox', 'CollapsibleGroupBox', 'ConsoleWidget', 'CustomStatusBar',
           'DetectorManagerWidget', 'DragNDropComboBox', 'DragNDropListView', 'FileInfoDialog',
           'HeaderDialog', 'HistoryLineEdit', 'LoadImagesDialog', 'MPLBetterCanvas', 'MPLHistogramCanvas',
           'DarkPalette', 'LightPalette', 'SaveImagesDialog', 'SettingsDialog']

from .BatchDialog import BatchDialog
from .ClickHoldComboBox import ClickHoldComboBox
from .CollapsibleGroupBox import CollapsibleGroupBox
from .ConsoleWidget import ConsoleWidget
from .CustomStatusBar import CustomStatusBar
from .DetectorManagerWidget import DetectorManagerWidget
from .DragNDropComboBox import DragNDropComboBox
from .DragNDropListView import DragNDropListView
from .FileInfoDialog import FileInfoDialog
from .HeaderDialog import HeaderDialog
from .HistoryLineEdit import HistoryLineEdit
from .LoadImagesDialog import LoadImagesDialog
from .MPLBetterCanvas import MPLBetterCanvas
from .MPLHistogramCanvas import MPLHistogramCanvas
from .Palletes import DarkPalette, LightPalette
from .SaveImagesDialog import SaveImagesDialog
from .SettingsDialog import SettingsDialog
try:
    import vispy
    from .VisPyCanvas import VisPyCanvas
    __all__ += ['VisPyCanvas']
except ImportError:
    pass
