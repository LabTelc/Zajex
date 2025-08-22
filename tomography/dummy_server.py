import socket
import threading

HOST = 'localhost'
PORT = 8080
from Socket import recv_unpack_message

def handle_client(conn, addr):
    print('Connected by', addr)
    while True:
        func_code, status_code, payload = recv_unpack_message(conn)
        print('Received from {}: {}:{}:{}'.format(addr, func_code, status_code, payload))
    conn.close()
    print('Connection closed for', addr)

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print('Server listening on port', PORT)

    while True:
        conn, addr = server_socket.accept()
        client_thread = threading.Thread(target=handle_client, args=(conn, addr))
        client_thread.daemon = True
        client_thread.start()

if __name__ == '__main__':
    start_server()
