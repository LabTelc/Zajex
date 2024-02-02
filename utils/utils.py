import os


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
    elif ft in ["png", "jpg", "jpeg", 'txt', 'raw']:
        return True
    else:
        return None
