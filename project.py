import socket
import os
import mimetypes
import logging
from datetime import datetime

HOST = '127.0.0.1'
PORT = 8080
WEB_ROOT = './www'

# Configura il logging su file
logging.basicConfig(
    filename='server.log',
    level=logging.INFO,
    format='[%(asctime)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def log_accesso(method, path, code):
    """Registra l'accesso nel file di log e in console."""
    message = f"{method} {path} -> {code}"
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")
    logging.info(message)

def get_content_type(file_path):
    type_, _ = mimetypes.guess_type(file_path)
    return type_ or 'application/octet-stream'

def handle_request(conn):
    request = conn.recv(1024).decode()
    if not request:
        conn.close()
        return

    lines = request.split('\r\n')
    request_line = lines[0].split()
    
    if len(request_line) < 3:
        conn.close()
        return

    method, path, _ = request_line

    if method != 'GET':
        response = "HTTP/1.1 405 Method Not Allowed\r\n\r\n"
        conn.sendall(response.encode())
        log_accesso(method, path, 405)
        conn.close()
        return

    if path == '/':
        path = '/index.html'

    file_path = os.path.join(WEB_ROOT, path.lstrip('/'))

    if os.path.isfile(file_path):
        with open(file_path, 'rb') as f:
            content = f.read()
        content_type = get_content_type(file_path)
        header = (
            "HTTP/1.1 200 OK\r\n"
            f"Content-Type: {content_type}\r\n"
            f"Content-Length: {len(content)}\r\n"
            "Connection: close\r\n\r\n"
        )
        conn.sendall(header.encode() + content)
        log_accesso(method, path, 200)
    else:
        response = (
            "HTTP/1.1 404 Not Found\r\n"
            "Content-Type: text/html\r\n"
            "Connection: close\r\n\r\n"
            "<h1>404 Not Found</h1>"
        )
        conn.sendall(response.encode())
        log_accesso(method, path, 404)

    conn.close()

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen(5)
        print(f"Server attivo su http://{HOST}:{PORT}")

        while True:
            conn, addr = server_socket.accept()
            handle_request(conn)

if __name__ == '__main__':
    start_server()