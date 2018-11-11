from socket import timeout
import socket
import ssl

CHAR_ENCODING = 'utf-8'

def init_socket(host, port):
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.connect((host, port)) 
    conn.settimeout(1)
    if port == 443: # For HTTPS connections
        conn = ssl.wrap_socket(conn)  
    return conn

def get_status(response):
    status_line = split_first_match(response, '\r\n')[0]
    status_code = status_line.split(' ')[1]
    return int(status_code)

def split_first_match(s, match):
    if match in s:
        return s.split(match, 1)
    else:
        return [s, '']

def create_request_header(url, method, header_dict, body=''):
    url_parts = split_first_match(url, '/')
    host, path = url_parts
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
            response += data.decode(CHAR_ENCODING)
    except timeout:
        pass
    return response   
        
def get_request(conn, url, header_dict):
    get_string = create_request_header(url, 'GET', header_dict)
    send_request(conn, get_string)
    response = receive_response(conn)
    status = get_status(response)
    if status >= 400:
        return None
    html_doc = split_first_match(response, '\r\n\r\n')[1]
    return html_doc

def post_request(conn, url, header_dict, body):
    post_string = create_request_header(url, 'POST', header_dict, body)
    send_request(conn, post_string)
    response = receive_response(conn)
    return response