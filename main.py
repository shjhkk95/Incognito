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
    #do bfs
    return 0

def crawl_dfs(initial_link):
    return 0

if __name__ == '__main__':
    web_crawler()
