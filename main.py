import requests
import password_generator
import html_parser

from bs4 import BeautifulSoup
import socket
import collections

password_list = []
MAX_DEPTH = 0

class Node:
    def __init__(self, link, depth):
        self.link = link
        self.depth = depth
    

def web_crawler():
    print('Hello Web Crawler')

    print(password_generator.generate_password_list(["leet", "code", "hacker"]))

def crawl_bfs(initial_link):
    # Add initial_link to the dequeue
    # Add URL to seen set
    seen, form_urls, queue = set(), set(), collections.deque(Node(initial_link, 0))

    # While queue is not empty
    while queue:
        node = queue.popleft()
        seen.add(node.link)
        # TODO Make GET request to the first element in queue
        html_text = requests.get_request(node.link)

        found_links = []
        # Use BeautifulSoup to parse:
        soup = BeautifulSoup(html_text, 'lxml')
            # TODO Get list of links
            # TODO Get list of keywords

            # TODO Was a form found

        # For each link in list of link
        for child in range(len(found_links)):
            # If the link is not in seen set
            if child not in seen:
                # Add link to seen
                seen.add(child)
                # Add link to queue
                queue.append(Node(child, node.depth + 1))


                # If a form was seen at this link
                if form_found is True:
                    # Add link to form url list
                    form_urls.add(child)
                    # Set form_found to false
                    form_found = False

    return 0

def crawl_dfs(link, depth, seen_links):
    # Get HTML
    html_text = requests.get_request(link)

    # Parse HTML
    parser = html_parser.HTMLParser(html_text)
    found_links = parser.extract_links()
    print(found_links)
    # Get Links into a list

    # For each Link, if link not in Seen, crawl_dfs
    if depth <= MAX_DEPTH:
        for found_link in found_links:
            if found_link not in seen_links:
                seen_links.add(found_link)
                crawl_dfs(found_link, depth + 1, seen_links)
    return 0


def html_parsing(html_text):
    return 0

if __name__ == '__main__':
    #web_crawler()
    seen_links = []
    crawl_dfs("http://18.219.249.115/", 0, seen_links)
