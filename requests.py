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
    status_line = response.split('\r\n', 1)[0]
    status_code = status_line.split(' ')[1]
    return int(status_code)

def extract_url_parts(url):
    port = 80 # Default to HTTP
    path = ''
    
    if '://' in url:
        url_parts = url.split('://', 1)
        protocol = url_parts[0]
        if (protocol == 'https'):
            port = 443
        url = url_parts[1] # Process rest of url
            
    host_and_path = url.split('/', 1)
    host = host_and_path[0]
    
    if len(host_and_path) != 1:
        path = host_and_path[1]
    
    # Check to see if port number is specified
    if ':' in host:
        host_and_port = host.split(':', 1)
        host = host_and_port[0]
        try:
            port = int(host_and_port[1])
        except ValueError:
            pass

    return host, path, port

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
    send_request(conn, get_string)
    response = receive_response(conn)
    if len(response) == 0:
        return None
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
    send_request(conn, post_string)
    response = receive_response(conn)
    conn.close()
    return response