import requests
import password_generator
from bs4 import BeautifulSoup
import socket

def web_crawler():
    print('Hello Web Crawler')
    requests.get_request()
    requests.post_request()

    print(password_generator.generate_password_list(["leet", "code", "hacker"]))

if __name__ == '__main__':
    web_crawler()
