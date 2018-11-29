from bs4 import BeautifulSoup
from nltk import word_tokenize

class HTMLParser:

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

            tokens = word_tokenize(self.html_doc)
            
            for word in tokens:
                if word.isalpha() and len(word) > 1:
                    words.add(word)
        
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