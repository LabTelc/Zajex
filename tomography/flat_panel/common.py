from tomography.Socket import send_message
from .FlatPanelEnums import ErrorCodes, FunctionCode


def perform_function_call(sock, function, *args, **kwargs):
    ret = function(*args)
    response = None
    name = kwargs["name"] if "name" in kwargs else ""
    if isinstance(ret, tuple):
        ret, response = ret[0], ret[1:]
    if ret != 0:
        print("Error in {} call: {}".format(function, ErrorCodes.name(ret)))
        send_message(sock, getattr(FunctionCode, function.__name__), ret, name)
        if "failure" in kwargs:
            exit(1)
    else:
        print("Function {}{} executed successfully.".format(function.__name__, args))
        send_message(sock, getattr(FunctionCode, function.__name__), ret, name)
    return response
