from url_utils import extract_url_parts
from socket import timeout
import socket
import ssl

CHAR_ENCODING = 'utf-8'

def init_socket(host, port):
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.connect((host, port)) 
    conn.settimeout(0.001)
    if port == 443: # For HTTPS connections
        conn = ssl.wrap_socket(conn)  
    return conn

def get_status(response):
    status_line = response.split('\r\n', 1)[0]
    status_code = status_line.split(' ')[1]
    return int(status_code)

def create_request_header(url, method, header_dict, body=''):
    host, path, _ = extract_url_parts(url)
    header = method + ' /' + path + ' HTTP/1.1\r\nHost: ' + host + '\r\n'
    for k, v in header_dict.items():
        header += (k + ': ' + v + '\r\n')
    header += '\r\n'
    if method == 'POST':
        header += body
    return header

def send_request(conn, header):
    conn.sendall(bytes(header, CHAR_ENCODING))

def receive_response(conn):
    response = ''
    data = None
    try:
        while data != b'':
            data = conn.recv(1024)
            response += data.decode(CHAR_ENCODING, 'ignore')
    except timeout:
        pass
    return response   
        
def get_request(url, header_dict):
    host, _, port = extract_url_parts(url)
    conn = init_socket(host, port)
    get_string = create_request_header(url, 'GET', header_dict)
    response = ''
    while len(response) == 0:
        send_request(conn, get_string)
        response = receive_response(conn)
    status = get_status(response)
    if status >= 400:
        return None
    html_doc = response.split('\r\n\r\n', 1)[1]
    conn.close()
    return html_doc

def post_request(url, header_dict, body):
    host, _, port = extract_url_parts(url)
    conn = init_socket(host, port)
    post_string = create_request_header(url, 'POST', header_dict, body)
    response = ''
    while len(response) == 0:
        send_request(conn, post_string)
        response = receive_response(conn)
    conn.close()
    return response