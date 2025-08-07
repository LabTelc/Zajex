import struct
import hashlib
import numpy as np
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

from utils import get_config

config = get_config()["Server"]
block_size = int(config["block_size"])


class SocketDataType:
    NONE = 0x00
    INT = 0x01
    FLOAT = 0x02
    STRING = 0x03
    NUMPY_ARRAY = 0x04
    COMMAND = 0x05


class SocketStatusCode:
    OK = 0
    ERROR = 1
    UNKNOWN = 2


def pad(data):
    pad_len = block_size - len(data) % block_size
    if isinstance(data, unicode):  # Python 2
        data = data.encode('utf-8')
    return data + bytes(bytearray([pad_len] * pad_len))


def unpad(data):
    pad_len = data[-1] if isinstance(data[-1], int) else ord(data[-1])
    return data[:-pad_len]


def derive_key(password):
    return hashlib.sha256(password.encode('utf-8')).digest()


def encrypt(data, password=config["password"]):
    key = derive_key(password)
    iv = get_random_bytes(block_size)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return iv + cipher.encrypt(pad(data))


def decrypt(data, password=config["password"]):
    key = derive_key(password)
    iv = data[:block_size]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(data[block_size:]))


def recv_all(conn, n):
    buf = b''
    while len(buf) < n:
        chunk = conn.recv(n - len(buf))
        if not chunk:
            raise Exception("Connection lost")
        buf += chunk
    return buf


def pack_message(func_code, status_code, payload):
    # Determine msg_type based on payload type
    if isinstance(payload, int):
        msg_type = SocketDataType.INT
        payload_bytes = struct.pack('!q', payload)
    elif isinstance(payload, float):
        msg_type = SocketDataType.FLOAT
        payload_bytes = struct.pack('!d', payload)
    elif isinstance(payload, (str, bytes)):
        msg_type = SocketDataType.STRING
        if isinstance(payload, str):
            payload_bytes = payload.encode('utf-8')
        else:
            payload_bytes = payload
    elif isinstance(payload, np.ndarray):
        msg_type = SocketDataType.NUMPY_ARRAY
        payload_bytes = pack_numpy_array(payload)
    elif payload is None:
        msg_type = SocketDataType.NONE
        payload_bytes = b''
    else:
        msg_type = SocketDataType.COMMAND
        if isinstance(payload, str):
            payload_bytes = payload.encode('utf-8')
        else:
            payload_bytes = bytes(payload)
    encrypted = encrypt(payload_bytes)
    header = struct.pack('!IIBI', func_code, status_code, msg_type, len(encrypted))
    return header + encrypted


def recv_unpack_message(conn):
    header = recv_all(conn, 13)  # 4 + 4 + 1 + 4
    func_code, status_code, msg_type, size = struct.unpack('!IIBI', header)
    encrypted_payload = recv_all(conn, size)
    payload_bytes = decrypt(encrypted_payload)

    if msg_type == SocketDataType.INT:
        payload = struct.unpack('!q', payload_bytes)[0]
    elif msg_type == SocketDataType.FLOAT:
        payload = struct.unpack('!d', payload_bytes)[0]
    elif msg_type == SocketDataType.STRING or msg_type == SocketDataType.COMMAND:
        try:
            payload = payload_bytes.decode('utf-8')
        except Exception:
            payload = payload_bytes
    elif msg_type == SocketDataType.NUMPY_ARRAY:
        payload = unpack_numpy_array(payload_bytes)
    elif msg_type == SocketDataType.NONE:
        payload = None
    else:
        payload = payload_bytes
    return func_code, status_code, payload


def send_message(sock, func_code, status_code, message):
    msg = pack_message(func_code, status_code, message)
    sock.sendall(msg)


def pack_numpy_array(arr):
    if not isinstance(arr, np.ndarray):
        raise TypeError("Input must be a numpy array")
    shape = arr.shape
    dtype = arr.dtype
    flat = arr.flatten()
    data = struct.pack('!IIi', shape[0], shape[1], dtype.num) + flat.tobytes()
    return data


def unpack_numpy_array(data):
    shape0, shape1, dtype_num = struct.unpack('!IIi', data[:12])
    dtype = np.dtype(np.sctypeDict[dtype_num])
    flat = np.frombuffer(data[12:], dtype=dtype)
    arr = flat.reshape((shape0, shape1))
    return arr
