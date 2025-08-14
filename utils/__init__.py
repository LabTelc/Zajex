import sys

if sys.version[0] == '2':
    from .utils import get_config
else:
    from .global_vars import *
    from .ImageSaverThread import ImageSaverThread
    from .ImageLoaderThread import ImageLoaderThread
    from .CustomPanZoomCamera import CustomPanZoomCamera
    from .utils import *
