from html_parser import HTMLParser
from requests import extract_url_parts, get_request, post_request
import password_generator
import collections

password_list = []
MAX_DEPTH = 0

class Node:
    def __init__(self, url, depth):
        self.url = url
        self.depth = depth
    

def web_crawler():
    print('Hello Web Crawler')
    url = '18.219.249.115'
    _, _, port = extract_url_parts(url)
    
    # Add protocol to url
    if port == 80 or 'http://' in url:
        url = 'http://' + url
    elif port == 443 or 'https://' in url:
        url = 'https://' + url

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
    # Add start URL to the deque and set of seen URLs
    seen = set()
    queue = collections.deque()
    keywords = set()
    form_url = None
    # Add start URL to the deque and set of seen URLs
    start_node = Node(start_url, 0)
    queue.append(start_node)
    seen.add(start_node.url)

    # While queue is not empty
    while queue:
        node = queue.popleft()
        print('Depth ' + str(node.depth) + ': ' + node.url)
        
        # Make GET request to the first element in queue        
        html_doc = get_request(node.url, header_dict)
        if html_doc is not None:
            parser = HTMLParser(html_doc)

            # Retrieve set of URLs reachable from current node 
            linked_urls = parser.extract_urls()

            # Extract and add words from current page to the set of keywords
            keywords |= parser.extract_words()
            
            if form_url is None:
                form_found = parser.detect_login_form()
                if form_found:
                    form_url = node.url

            for url in linked_urls:
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
    