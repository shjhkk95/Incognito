import requests
import password_generator

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

def crawl_dfs(initial_link):
    return 0


def html_parsing(html_text):


if __name__ == '__main__':
    web_crawler()
