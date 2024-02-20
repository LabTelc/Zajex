import os
from PIL import Image
import numpy as np
import tifffile


def validate_input(filepath, parameters):
    if not os.path.exists(filepath) or not os.path.isfile(filepath):
        return None
    ft = filepath.split(".")[-1]
    if ft == "bin":
        size = os.path.getsize(filepath)
        if parameters.width > 0 and parameters.height > 0:
            dtype = int(parameters.dtype.split("t")[-1]) // 8
            if size / (parameters.width * parameters.height * dtype) == 1:
                return True
            else:
                return False
        else:
            return False
    elif ft in ["png", "jpg", "jpeg", 'txt', 'raw', 'tiff', 'tif']:
        return True
    else:
        return None


def save_jpg(mat, name, path, **kwargs):
    mat = mat.astype(np.uint8)
    im = Image.fromarray(mat)
    im.save(f"{path}/{name}.jpg")


def save_png(mat, name, path, **kwargs):
    mat = mat.astype(np.uint8)
    im = Image.fromarray(mat)
    im.save(f"{path}/{name}.png")


def save_tif(mat, name, path, **kwargs):
    mat = mat.astype(np.uint16)
    tifffile.imwrite(f"{path}/{name}.tif", mat, photometric='minisblack')


def save_raw(mat, name, path, **kwargs):
    if "dtype" in kwargs:
        dtype = kwargs["dtype"]
        mat = mat.astype(dtype)
    header = kwargs["header"]
    header_packed = header.getPacked()[1]

    with open(f"{path}/{name}.raw", 'wb') as f:
        f.write(header_packed)
        f.write(np.ascontiguousarray(mat))


def save_txt(mat, name, path, **kwargs):
    if "dtype" in kwargs:
        dtype = kwargs["dtype"]
        mat = mat.astype(dtype)
    if np.issubdtype(mat.dtype, np.integer):
        fmt = '%d'  # integer format
    elif np.issubdtype(mat.dtype, np.floating):
        fmt = '%.5f'  # float format to 5 decimal places
    else:
        raise ValueError("Unsupported data type for array")
    np.savetxt(f"{path}/{name}.txt", mat, fmt=fmt,
               header=f"Numpy array of shape {mat.shape} of type {mat.dtype}")


def save_bin(mat, name, path, **kwargs):
    if "dtype" in kwargs:
        dtype = kwargs["dtype"]
        mat = mat.astype(dtype)
    mat.tofile(f"{path}/{name}.bin")


def get_save_image(filetype):
    if filetype == "tif":
        return save_tif
    elif filetype == "jpg":
        return save_jpg
    elif filetype == "png":
        return save_png
    elif filetype == "raw":
        return save_raw
    elif filetype == "bin":
        return save_bin
    elif filetype == "txt":
        return save_txt
