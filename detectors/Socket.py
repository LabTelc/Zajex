import struct
import numpy as np


class SocketDataType:
    STRING = 0
    INT = 1
    FLOAT = 2
    UINT16_ARRAY = 3


class SocketStatusCode:
    OK = 0
    ERROR = 1
    UNKNOWN = 2

def send_response(conn, response):
    try:
        if isinstance(response, np.ndarray):
            status = 1
            type_code = 2
            arr = response.astype(np.float32)
            length = len(arr)
            header = struct.pack('BBI', status, type_code, length)
            payload = struct.pack('%sf' % length, *arr)
            conn.sendall(header + payload)
        elif isinstance(response, (int, float)):
            status = 1
            type_code = 1
            payload = struct.pack('BBf', status, type_code, float(response))
            conn.sendall(payload)
        else:
            # Send error
            status = 0
            type_code = 0
            error_msg = "Invalid response"
            conn.sendall(struct.pack('BB', status, type_code))
    except Exception as e:
        conn.sendall(struct.pack('BB', 0, 0))


def recv_all(sock, size):
    data = b''
    while len(data) < size:
        packet = sock.recv(size - len(data))
        if not packet:
            raise Exception("Connection closed")
        data += packet
    return data

def receive_response(sock):
    # Peek first two bytes: status and type_code
    header = recv_all(sock, 2)
    status, type_code = struct.unpack('BB', header)

    if status == 0:
        return "ERROR in response"

    if type_code == 1:
        # It's a number
        payload = recv_all(sock, 4)
        result = struct.unpack('f', payload)[0]
        return result
    elif type_code == 2:
        # It's an array
        length_bytes = recv_all(sock, 4)
        length = struct.unpack('I', length_bytes)[0]
        payload = recv_all(sock, 4 * length)
        result = struct.unpack('%sf' % length, payload)
        return result
    else:
        return "Unknown type"