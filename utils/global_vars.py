from dataclasses import dataclass

supportedLoadFormats = ['raw', 'bin', 'txt', 'tif', 'jpg', 'png']
supportedSaveFormats = ['raw', 'bin', 'txt', 'tif', 'jpg']
supportedDataTypes = ['int8', 'int16', 'int32', 'int64',
                      'uint8', 'uint16', 'uint32', 'uint64',
                      'float8', 'float16', 'float32', 'float64']

limits_dict = {0: "min - max", 1: "1 - 99", 2: "5 - 95", 3: "(min+1) - (max-1)"}
cmaps_list = ['gray', 'viridis', 'plasma', 'inferno', 'magma', 'cividis', 'Greys', 'Purples', 'Blues', 'Greens',
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

@dataclass
class LogTypes:
    Log = 0
    Warning = 1
    Error = 2
