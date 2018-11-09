from socket import timeout
import socket
import ssl

CHAR_ENCODING = 'utf-8'

def init_socket(url, port):
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.connect((url, port)) 
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

def create_request_header(url, method, header_dict):
    url_parts = split_first_match(url, '/')
    host, path = url_parts
    header = method + ' /' + path + ' HTTP/1.1\r\nHost: ' + host + '\r\n'
    for k, v in header_dict.items():
        header += (k + ': ' + v + '\r\n')
    header += '\r\n'
    return header

def send_request(conn, header):
    conn.sendall(bytes(header, CHAR_ENCODING))

def receive_response(conn):
    response = ''
    try:
        while True:
            data = conn.recv(1024)
            response += data.decode(CHAR_ENCODING)
    except timeout:
        pass
    return response    
        
def get_request(conn, url, header_dict):
    get_string = create_request_header(url, 'GET', header_dict)
    send_request(conn, get_string)
    response = receive_response(conn)
    html_doc = split_first_match(response, '\r\n\r\n')[1]
    #print(html_doc)
    return html_doc

"""
conn = init_socket('www.securitee.org', 443)
d = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246'}
get_request(conn, 'www.securitee.org/teaching/cse331/', d)
"""

def post_request(url):
    print('Making POST request')
