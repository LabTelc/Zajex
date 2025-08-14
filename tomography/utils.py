def get_perf_function_call(error_code, function_code, success, send_message):
    def perform_function_call(sock, function, *args, **kwargs):
        ret = function(*args)
        response = None
        if isinstance(ret, tuple):
            ret, response = ret[0], ret[1:]
        if isinstance(response, tuple) and len(response) == 1:
            response = response[0]
        if ret != success:
            print("Error in {} call: {}".format(function, error_code.name(ret)))
            send_message(sock, getattr(function_code, function.__name__), ret, response)
            if "failure" in kwargs:
                exit(1)
        else:
            print("Function {}{} executed successfully.".format(function.__name__, args))
            send_message(sock, getattr(function_code, function.__name__), ret, response)
        return response

    return perform_function_call


def get_config():
    try:
        import configparser
    except ImportError:
        import ConfigParser as configparser  # Python 2 fallback
    config = configparser.ConfigParser()
    config.read('utils/config.ini')
    return config


def ctypes_array_type_convert(data, new_type):
    return  (new_type * len(data))(*[new_type(x.value).value for x in data])
