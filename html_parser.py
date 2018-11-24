from bs4 import BeautifulSoup
from nltk import word_tokenize
from nltk.corpus import stopwords
from requests import get_request, get_status, init_socket, post_request

class HTMLParser:
    
    IGNORED_WORDS = set(stopwords.words('english'))
    TEXT_TAGS = ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li' , 'a']

    def __init__(self, html_doc):
        self.html_doc = html_doc
        self.soup = BeautifulSoup(html_doc, "html.parser")

    def extract_urls(self):
        urls = set()
        if self.html_doc is not None:
            
            for link in self.soup.find_all('a'):
                href = link.get('href')
            
                if href is not None:
                    urls.add(href)
        return urls

    def extract_words(self):
        words = set()
        if self.html_doc is not None:
            text = ''
            
            for tag in self.soup.find_all(self.TEXT_TAGS):
                duplicate = False
                
                # Make sure text was not added by a parent tag
                for parent in tag.parents:
                    if parent.name in self.TEXT_TAGS:
                        duplicate = True
                
                if not duplicate:    
                    text += tag.get_text() + '\n'

            tokens = word_tokenize(text)
            
            for word in tokens:
                if word.isalpha() and len(word) > 1 and word.lower() not in self.IGNORED_WORDS:
                    words.add(word.lower())
        
        return words

    def detect_login_form(self):
        for form in self.soup.find_all('form'):
            form_id = form.get('id')
            form_name = form.get('name')
            if (form_id and 'login' in form_id) or (form_name and 'login' in form_name):
                return True
        return False

    def create_login_string(self, user, password):
        login = ''
        form_present = self.detect_login_form()
        
        if form_present:               
            for tag in self.soup.find_all('input'):                         
                input_type = tag.get('type')

                if input_type is not None:
                    if 'text' in input_type or 'email' in input_type:
                        # Extract name of username input field and append given username to string
                        login += tag.get('name') + '=' + user + '&'
                    
                    elif 'password' in input_type:
                        # Extract name of password input field and append given password to string
                        login += tag.get('name') + '=' + password
                        break # String is finished after password
        return login

"""
get = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246'}

html_doc = get_request('18.219.249.115/wp-login.php', get)
parser = HTMLParser(html_doc)

user = 'user'
password = 'IncognitoWebCrawl'
login = parser.create_login_string(user, password)
post = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Content-Length': str(len(login))}

response = post_request('18.219.249.115/wp-login.php', post, login)
if get_status(response) == 302:
    print('Login Succeeded')
else:
    print('Login Failed')
"""