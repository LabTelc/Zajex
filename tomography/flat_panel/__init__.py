import sys
from .common import perform_function_call
from .FlatPanelEnums import *
if sys.version[0] == '2':
    from .FlatPanelFunctions import *
    from .FlatPanelStructures import *