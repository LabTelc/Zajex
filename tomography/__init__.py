import sys
if sys.version_info[0] == 3:
    from .ui_elements_classes.TomographyManagerWidget import TomographyManagerWidget
    from .TomographyManagerThread import TomographyManagerThread