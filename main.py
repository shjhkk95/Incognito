import requests
import password_generator

def web_crawler():
    print('Hello Web Crawler')
    requests.get_request()
    requests.post_request()
    password_generator.convert_to_leetspeak()
    password_generator.reverse_password()


if __name__ == '__main__':
    web_crawler()
