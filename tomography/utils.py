def get_perf_function_call(error_code, function_code, success, send_message):
    def perform_function_call(sock, function, *args, **kwargs):
        log = kwargs.pop('log', True)
        response_type = kwargs.pop('response', "response")
        ret = function(*args)
        response = None
        if isinstance(ret, tuple):
            ret, response = ret[0], ret[1:]
        if isinstance(response, tuple) and len(response) == 1:
            response = response[0]
        if ret != success:
            print("Error in {} call: {}".format(function, error_code.name(ret)))
            fn_name = function.__name__ if not function.__name__.endswith("_local") else function.__name__[:-len("_local")]
            send_message(sock, getattr(function_code, fn_name), ret, response)
            if "failure" in kwargs:
                exit(1)
        else:
            if log:
                print("Function {}{} executed successfully.".format(function.__name__, args[1:]))
            fn_name = function.__name__ if not function.__name__.endswith("_local") else function.__name__[:-len("_local")]
            if response_type == "response":
                send_message(sock, getattr(function_code, fn_name), ret, response)
            else:
                send_message(sock, getattr(function_code, fn_name), ret, args[1:])
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

