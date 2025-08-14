# -*- coding: utf-8 -*-
# python 2.7 #
import sys

if sys.version[0] != '2':
    raise SystemError("Python 3 is not supported.")

import select
import time
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread

from soloist import *
from Socket import send_message, recv_unpack_message
from utils import get_config, get_perf_function_call

config = dict(get_config().items("Server"))
perform_function_call = get_perf_function_call(ErrorCode, FunctionCode, 1, send_message)

sock = socket(AF_INET, SOCK_STREAM)
try:
    print("Connecting to server at {}:{}".format(config["host"], config["port"]))
    sock.connect((config["host"], int(config["port"])))
except Exception as e:
    print("Cannot connect to server:", e)
    exit(1)

##### Initialize table #####
send_message(sock, FunctionCode.ServerConnect, 1, "Soloist")
print("Initializing table...")
handles, count = perform_function_call(sock, connect, failure=True)
print("Detected {} tables. Using only the first one...".format(count))
handle = handles[0]
perform_function_call(sock, enable, handle, failure=True)
print("Table ready for commands.")


def feedback_thread():
    while True:
        try:
            perform_function_call(sock, get_program_position_feedback, handle)
            perform_function_call(sock, get_axis_status, handle)
            time.sleep(0.1)
        except Exception as e:
            print("Error in feedback thread:", e)
            break


feedback = Thread(target=feedback_thread)
feedback.daemon = True
feedback.start()

### Waiting for commands and sending feedback ###
while True:
    try:
        ready_to_read, _, _ = select.select([sock], [], [], float(config["timeout"]))
        if ready_to_read:
            try:
                func_code, status_code, message = recv_unpack_message(sock)
                if message[0] is None:
                    message = []
                perform_function_call(sock, globals()[FunctionCode.name(func_code)], handle, *message)
            except Exception as e:
                print("Cannot unpack message:", e)
                break
    except KeyboardInterrupt:
        break

print("Closing socket...")
sock.close()
print("Closed gracefully.")
