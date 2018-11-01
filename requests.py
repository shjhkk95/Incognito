from socket import timeout
import socket
import ssl

def init_socket(url, port):
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.connect((url, port)) 
    conn.settimeout(1)
    if port == 443:
        conn = ssl.wrap_socket(conn)  
    return conn

def get_request(url):
    url_parts = url.split('/', 1)
    host = url_parts[0] if '/' in url else url
    path = url_parts[1] if '/' in url else ''
    conn = init_socket(host, 443)
    get_string = 'GET /' + path + ' HTTP/1.1\r\nHost: ' + host + '\r\n\r\n'
    conn.sendall(bytes(get_string, 'utf-8'))
    try:
        html_doc = ''
        while True:
            data = conn.recv(1024)
            html_doc += data.decode("utf-8")
    except timeout:
        pass
    print(html_doc)
    return html_doc

get_request('www.securitee.org')

def post_request(url):
    conn = init_socket(url)
    print('Making POST request')
