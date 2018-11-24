from html_parser import HTMLParser
from requests import extract_url_parts, get_request, post_request
import password_generator
import collections

password_list = []
MAX_DEPTH = 10

class Node:
    def __init__(self, url, depth):
        self.url = url
        self.depth = depth
    
def add_protocol(url, port):
    # Add protocol to url
    if port == 80 and 'http://' not in url:
        url = 'http://' + url
    elif port == 443 and 'https://' not in url:
        url = 'https://' + url 
    return url   

def add_duplicate_url(url, seen):
    # If the URL has a trailing slash, add the URL without the slash to set of seen nodes
    if url[-1] == '/':
        seen.add(url[:-1])
        
    # Else the URL doesn't have a trailing slash and add the URL with a slash to set of seen nodes
    else:
        seen.add(url + '/')       

def reformat_url(url, base_url=''):       
    # If base URL is given, prepend it to the given URL
    if base_url != '':      
        
        # Ignore relative URLs starting with '#'
        if '#' not in url:
            
            host, _, port = extract_url_parts(base_url)

            # Remove trailing slash from base url
            if base_url[-1] == '/':
                base_url = base_url[:-1]
                
            # Look for URLs starting with "./" or "//"
            if len(url) >= 2:
                # Remove "./" from the start of the URL if present
                if url[0:2] == './':
                    url = url[2:]

                # If URL starts with "//", prepend the appropriate protocol
                elif url[0:2] == '//':
                    base_url = add_protocol('', port)
                    url = url[2:]
                    if len(base_url) > 0:
                        base_url = base_url[:-1]

                # Remove "/" from the start of the URL if present
                elif url[0] == '/':
                    url = url[1:]
                    base_url = host

            if url not in base_url:
                url = base_url + '/' + url
    else:
        _, _, port = extract_url_parts(url)
        url = add_protocol(url, port)
    return url

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

def web_crawler():
    url = 'http://18.219.249.115/'
    url = reformat_url(url)
    
    keywords_bfs, forms_bfs, seen_bfs = crawl_bfs(url, {})
    print('\n\nKeywords:', keywords_bfs, '\n\nForm:', forms_bfs, '\n\nSeen:', seen_bfs, sep=' ')

    print()

    keywords_dfs, forms_dfs, seen_dfs = crawl_dfs(url, {})
    print('\n\nKeywords:', keywords_dfs, '\n\nForm:', forms_dfs, '\n\nSeen:', seen_dfs, sep=' ')

if __name__ == '__main__':
    web_crawler()
    