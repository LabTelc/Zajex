from utils import get_config
import struct
import numpy as np
import hashlib
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
config = get_config()["Server"]


class SocketDataType:
    STRING = 0
    INT = 1
    FLOAT = 2
    NUMPY_ARRAY = 3
    COMMAND = 4


class SocketStatusCode:
    OK = 0
    ERROR = 1
    UNKNOWN = 2

def pad(data):
    pad_len = config["block_size"] - len(data) % config["block_size"]
    return data + bytes([pad_len] * pad_len)

def unpad(data):
    return data[:-ord(data[-1])] if isinstance(data[-1], str) else data[:-data[-1]]

def derive_key(password):
    return hashlib.sha256(password.encode('utf-8')).digest()

def encrypt(data):
    key = derive_key(config["password"])
    iv = get_random_bytes(config["block_size"])
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return iv + cipher.encrypt(pad(data))

def decrypt(data):
    key = derive_key(config["password"])
    iv = data[:config["block_size"]]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(data[config["block_size"]:]))

def recv_all(conn, n):
    buf = b''
    while len(buf) < n:
        chunk = conn.recv(n - len(buf))
        if not chunk:
            raise Exception("Connection lost")
        buf += chunk
    return buf

def handle_client(conn):
    while True:
        header = recv_all(conn, 5)
        status, msg_type, size = struct.unpack('!BBI', header)
        encrypted_payload = recv_all(conn, size)
        payload = decrypt(encrypted_payload)

        if msg_type == SocketDataType.INT:
            val = struct.unpack('!i', payload)[0]
            print("Received int:", val)
        elif msg_type == SocketDataType.FLOAT:
            val = struct.unpack('!f', payload)[0]
            print("Received float:", val)
        elif msg_type == SocketDataType.STRING:
            print("Received string:", payload.decode('utf-8'))
        elif msg_type == SocketDataType.NUMPY_ARRAY:
            shape = struct.unpack('!II', payload[:8])
            flat = np.frombuffer(payload[8:], dtype=np.uint16)
            arr = flat.reshape(shape)
            print("Received numpy array of shape", shape)
        elif msg_type == SocketDataType.COMMAND:
            print("Received command:", payload.decode('utf-8'))
        else:
            print("Unknown message type:", msg_type)


def send_response(conn, status, response):
    try:
        if isinstance(response, np.ndarray):
            type_code = 2
            arr = response.astype(np.float32)
            length = len(arr)
            header = struct.pack('BBI', status, type_code, length)
            payload = struct.pack('%sf' % length, *arr)
            conn.sendall(header + payload)
        elif isinstance(response, (int, float)):
            type_code = 1
            payload = struct.pack('BBf', status, type_code, float(response))
            conn.sendall(payload)
        elif isinstance(response, str):
            type_code = 0
            encoded = response.encode('utf-8')
            length = len(encoded)
            header = struct.pack('BBI', status, type_code, length)
            conn.sendall(header + encoded)
    except Exception as e:
        conn.sendall(struct.pack('BB', 1, 0, e.args[0].encode('utf-8')))


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
        payload = recv_all(sock, 4)
        result = struct.unpack('f', payload)[0]
        return result
    elif type_code == 2:
        length_bytes = recv_all(sock, 4)
        length = struct.unpack('I', length_bytes)[0]
        payload = recv_all(sock, 4 * length)
        result = struct.unpack('%sf' % length, payload)
        return result
    else:
        return "Unknown type"