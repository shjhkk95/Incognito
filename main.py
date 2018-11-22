from html_parser import HTMLParser
from requests import extract_url_parts, get_request, post_request
import password_generator
import collections

password_list = []
MAX_DEPTH = 5

class Node:
    def __init__(self, url, depth):
        self.url = url
        self.depth = depth
    
def reformat_url(url, base_url=''):
    _, _, port = extract_url_parts(url)
    
    # If base URL is given, prepend it to the given URL
    if base_url != '':      
        # Ignore relative URLs starting with '#'
        if '#' not in url:
            # Remove trailing slash from base url
            if (base_url[-1] == '/'):
                base_url = base_url[:-1]
            
            # Remove starting slash from url
            if (url[0] == '/'):
                url = url[1:]

            if url not in base_url:
                url = base_url + '/' + url
    else:
        # Add protocol to url
        if port == 80 and 'http://' not in url:
            url = 'http://' + url
        elif port == 443 and 'https://' not in url:
            url = 'https://' + url
    return url

def web_crawler():
    print('Hello Web Crawler')
    url = '18.219.249.115'
    url = reformat_url(url)

    keywords, form_url = crawl_bfs(url, {})
    print(keywords)
    print(form_url)    

    """
    form_urls, found_keywords = set(), []
    crawl_bfs('18.219.115/', '18.219.249.115', 80, form_urls, found_keywords)
    conn = requests.init_socket("www.google.com",443)
    html_doc = requests.get_request(conn, "www.google.com", {})

    parser = html_parser.HTMLParser(html_doc)

    linkset = parser.extract_links()
    for link in linkset:
        print(link)

    queue = crawl_dfs("www.google.com", "www.google.com", 443)
    while (len(queue) > 0):
        print(queue.popleft())

    print(password_generator.generate_password_list(["leet", "code", "hacker"]))    
    """

def crawl_bfs(start_url, header_dict):
    form_url = None
    keywords = set()
    seen = set()
    queue = collections.deque()
    
    # Add start URL to the deque and set of seen URLs
    start_node = Node(start_url, 0)
    queue.append(start_node)
    seen.add(start_node.url)

    # While queue is not empty
    while queue:
        node = queue.popleft()
        print('Depth ' + str(node.depth) + ': ' + node.url)

        # If the URL has a trailing slash, add the URL without the slash to set of seen nodes
        if node.url[-1] == '/':
            seen.add(node.url[-1])
        # Else the URL doesn't have a trailing slash and add the URL with a slash to set of seen nodes
        else:
            seen.add(node.url + '/')   
        
        # Make GET request to the first element in queue        
        html_doc = get_request(node.url, header_dict)
        if html_doc is not None:
            parser = HTMLParser(html_doc)

            # Extract and add words from current page to the set of keywords
            keywords |= parser.extract_words()

            # Attempt to find form if not found yet
            if form_url is None:
                form_found = parser.detect_login_form()
                if form_found:
                    form_url = node.url
            
            # Add reachable URLs from current node if its depth < max depth
            if node.depth < MAX_DEPTH:
                # Retrieve set of URLs reachable from current node 
                linked_urls = parser.extract_urls()

                for url in linked_urls:
                    # Reformat if relative url given
                    if 'http' not in url:
                        url = reformat_url(url, node.url)                 

                    if url not in seen and start_url in url:
                        seen.add(url)
                        queue.append(Node(url, node.depth + 1))
        
    return keywords, form_url

def crawl_dfs(url, host_name, port):
    # Get HTML
    conn = requests.init_socket(host_name, port)
    html_text = requests.get_request(conn, url, {})
    queue = collections.deque([])

    crawl_def_helper(url, host_name, port, queue)
    
   
    return queue

#Traverse the Link in DFS manner and add to the queue
def crawl_def_helper(url, host_name, port, queue):

    print(url)
    conn = requests.init_socket(host_name, port)
    html_doc = requests.get_request(conn, url, {})
    if html_doc == None :
        queue.append(url)
        return
        
    parser = html_parser.HTMLParser(html_doc)
    #linkset = all the links that is found on current page
    linkset = parser.extract_links()
    linkset = linkset.difference(queue)

    if (len(linkset) ==0 ):
        queue.append(url)
        return
    
    ##dfs : add child into queue prior to current node.
    for link in linkset:
        crawl_def_helper(link, host_name, port, queue)

    queue.append(url)
    return

if __name__ == '__main__':
    web_crawler()
    