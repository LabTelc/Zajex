from dataclasses import dataclass
import numpy as np

supportedLoadFormats = ['bin', 'raw', 'txt', 'tif', 'jpg', 'png', 'pbf']
supportedSaveFormats = ['tif', 'raw', 'bin', 'txt', 'jpg', 'png']
save_formats_strings = {
    "raw": "EZRT raw file, version 2.5.0 (*.raw)",
    "bin": "Binary file (*.bin)",
    "txt": "ASCII text file (*.txt)",
    "tif": "TIFF file (*.tif)",
    "jpg": "JPEG image file (*.jpg)",
    "png": "PNG file (*.png)",
    "pbf": "PBF image file (*.pbf)",
}
supportedDataTypes = ['int8', 'int16', 'int32', 'int64',
                      'uint8', 'uint16', 'uint32', 'uint64',
                      'float8', 'float16', 'float32', 'float64']

supportedDataTypesByFileType = {
    "tif": ["uint8", "uint16", "uint32", "uint64",
            "int8", "int16", "int32", "int64",
            "float16", "float32", "float64"],
    "raw": ['int8', 'int16', 'int32', 'int64',
            'uint8', 'uint16', 'uint32', 'uint64',
            'float8', 'float16', 'float32', 'float64'],
    "bin": ['int8', 'int16', 'int32', 'int64',
            'uint8', 'uint16', 'uint32', 'uint64',
            'float16', 'float32', 'float64'],
    "jpg": ["uint8"],
    "png": ["uint8"],
    "txt": ['int8', 'int16', 'int32', 'int64',
            'uint8', 'uint16', 'uint32', 'uint64',
            'float8', 'float16', 'float32', 'float64'],
}

limits_dict = {0: "min - max",
               1: "1 - 99",
               2: "5 - 95",
               3: "0.1 - 99.9",
               4: "0.01 - 99.99",
               5: "0.001 - 99.999",
               6: "(min+1) - (max-1)"}

cmaps_list = ['gray', 'viridis', 'plasma', 'inferno', 'magma', 'cividis', 'jet']

cmaps_list_all = ['gray', 'viridis', 'plasma', 'inferno', 'magma', 'cividis', 'Greys', 'Purples', 'Blues', 'Greens',
              'Oranges', 'Reds', 'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 'BuPu', 'GnBu', 'PuBu', 'YlGnBu',
              'PuBuGn', 'BuGn', 'YlGn', 'binary', 'gist_yarg', 'gist_gray', 'gray', 'bone', 'pink', 'spring', 'summer',
              'autumn', 'winter', 'cool', 'Wistia', 'hot', 'afmhot', 'gist_heat', 'copper', 'PiYG', 'PRGn', 'BrBG',
              'PuOr', 'RdGy', 'RdBu', 'RdYlBu', 'RdYlGn', 'Spectral', 'coolwarm', 'bwr', 'seismic']

lFileTypeString = """
            Binary file (*.bin);;
            EZRT raw file, version 2.5.0 (*.raw);;
            ASCII txt file (*.txt);;
            PNG file (*.png);;
            JPG image (*.jpg);;
            TIFF file (*.tiff);;
            All files (*.*)
            """
rotation_list = ["0°", "90°", "180°", "270°"]

item_type = "application/x-qabstractitemmodeldatalist"


@dataclass
class LogTypes:
    Log = 0
    Warning = 1
    Error = 2


@dataclass
class Parameters:
    dtype: str = 'uint16'
    header: int = 0
    width: int = 0
    height: int = 0
    rotate: int = 0
    mirror_UD: bool = False
    mirror_LR: bool = False
    cmap: str = 'gray'
    from_zoom: bool = False
    last_dir: str = "./"
    show_axes: bool = False
    num_bins: int = 30
    ratio: float = 1 / np.e
    tiff_bit_depth: str = str(np.uint16)


@dataclass
class ImageObject:
    array: np.ndarray
    vmin: float
    vmax: float
    x_lim: tuple
    y_lim: tuple
    id_: int
    filepath: str
    mirror_UD: bool = False
    mirror_LR: bool = False
    rotation: int = 0
