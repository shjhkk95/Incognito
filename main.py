import requests
import password_generator
from bs4 import BeautifulSoup
import socket

password_list = []

def web_crawler():
    print('Hello Web Crawler')
    requests.get_request()
    requests.post_request()

    print(password_generator.generate_password_list(["leet", "code", "hacker"]))

def crawl_bfs(initial_link):
    # Make a GET request to initial_link

    # Get list of links and keywords on the webpage

    # Add keywords to

    # Check if the links are in the visited set

    # If they are not in the set, add them to the dequeue

    # Remove link from the head of the dequeue and 
    # call crawl_bfs

def crawl_dfs():
    # Do a dfs


if __name__ == '__main__':
    web_crawler()
