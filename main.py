import requests
import password_generator
import html_parser

from bs4 import BeautifulSoup
import socket
import collections

password_list = []

class Node:
    def __init__(self, link, depth):
        self.link = link
        self.depth = depth
    

def web_crawler():
    print('Hello Web Crawler')

    form_urls, found_keywords = set(), []
    crawl_bfs('18.219.115/', '18.219.249.115', 80, form_urls, found_keywords)

    print(password_generator.generate_password_list(["leet", "code", "hacker"]))

def crawl_bfs(initial_link, host_name, port, form_urls, found_keywords):
    # Add initial_link to the dequeue
    # Add URL to seen set
    seen, queue = set(), collections.deque(Node(initial_link, 0))

    # While queue is not empty
    while queue:
        node = queue.popleft()
        seen.add(node.link)
        # TODO Make GET request to the first element in queue
        conn = requests.init_socket(host_name, port)
        html_doc = requests.get_request(conn, node.link, {})
        conn.close()


        parser = html_parser.HTMLParser(html_doc)
        found_links = parser.extract_links()
        found_keywords.append(parser.extract_words())
        form_found = parser.detect_login_form()

        # For each link in list of link
        for link in range(len(found_links)):
            # TODO if the link will not naviagte us away
                # If the link is not in seen set
                if link not in seen:
                    # Add link to seen
                    seen.add(link)
                    # Add link to queue
                    queue.append(Node(initial_link + link, node.depth + 1))


                    # If a form was seen at this link
                    if form_found is True:
                        # Add link to form url list
                        form_urls.add(initial_link + link)
                        # Set form_found to false
                        form_found = False
    
    return 0

def crawl_dfs(initial_link):
    return 0


def html_parsing(html_text):
    return 0

if __name__ == '__main__':
    web_crawler()
