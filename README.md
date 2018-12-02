# Incognito

Incognito Web Crawler
	Github: https://github.com/shjhkk95/Incognito
Team members:
Brandon Chen - bndncn
Hong Jie Cen - HongCen
Nicholas Pirrello - nspirrello
Seokhoon Kim - shjhkk95

How we made our web crawler:

	The project is split into two parts. The first part is the web crawler itself which is written fully in Python 3. It utilizes BeautifulSoup, NLTK, and the Python Socket library. We tried to keep our web crawler source code as modular and clean as we could. Because of this our web crawler uses five different files - html_parser.py, password_generator.py, requests.py, url_utils.py, and main.py -  in conjunction with each other. The web crawler entry point is through main.py.  The second part of the project is our website to test the web crawler’s functionality. The test website is a wordpress site, consisting of generated HTML and CSS, that is hosted on Amazon Web Services.

GET and POST requests:
Both functions can be located in the requests.py file. In order to send these types of requests, the requests.py file contains the following functions. These requests are made by calling get_request and post_request. The GET request is necessary for retrieving the web page’s HTML. The POST request is needed to attempt a login form bruteforce.
		
init_socket: Opens a Python websocket connection with a specified host and port. If the port number resembles the SSL port number (443), the connection is wrapped with SSL.

receive_response: Takes in a websocket connection as a parameter, initializes an empty string to hold the entire response and listens to the socket connection for a length of 1024 bytes of response data. These bytes of data are then transformed into a string value which is then appended to the currently empty response string. This process repeats until either a end of response indicator is sent (byte value for an empty string) or the request suffers a timeout. Once either occurs, the response data is considered completed and it’s returned.

send_request: Takes in a websocket connection and the HTTP header we’ve created and sends the request to the URL that the socket is connected to.

get_status: Takes in a HTTP formatted response string and extracts the status code from the response header and returns it.

create_request_header: Takes in a URL, method type (GET or POST), the header data, and the body data if applicable (for POST requests). A request header following the HTTP protocol is created and returned.

get_request: Takes in a URL as a parameter, parses the host name and port from the URL and creates a websocket connection. Then a GET request header is created and the request is sent. We listen to the connection until either a timeout exception is thrown or we receive an end-of-response indicator. Then we extract the status code from the response string. If the status code is 400 or above the request was ‘unsuccessful’ (could have been Not Found, Internal Server Error, etc..). If the request was ‘successful’ we split the html part from the response string, close the connection, and return the html string.

post_request: Takes in a URL as a parameter, parses the host name and port from the URL and creates a websocket connection. Then a POST request header is created and the request is sent. We listen to the connection until either a timeout exception is thrown or we receive an end-of-response indicator. Then we close the websocket connection and return the entire response string. We’ll extract the status code later on.

Extracting keywords, links, and form:
In order to extract keywords, links, and detect forms we use BeautifulSoup by finding <a> tags for links. We use NLTK’s word tokenizer to extract words, and for form detection we look for form tags that contain an id with the value ‘login’. Each HTML page we encounter becomes a HTMLParser object.

extract_urls: Uses html page stored in class field ‘html_doc’ and finds all references to the <a> tag. We use the built in set data structure to make sure that duplicate links aren’t extracted from a single page.

extract_words: Uses the html page stored in the class field ‘html_doc’. We use NLTK’s word_tokenize function to extract keywords on a given webpage and then add the keywords that consist only of letters and are longer than a character long. The words extracted from the webpage are returned.

detect_login_form: Uses the html page stored in the class’ field ‘html_doc’ and finds all references to a form tag with the id or name value of ‘login’ and returns true or false depending on if one was found. This allows us to add this url where this page is located to a master ‘form_url’ list. This list is used by the form bruteforcer. 

create_login_string: Takes in a user string and password string as parameters. Uses the html page stored in the class field ‘html_doc’ and finds all references to an input tag within the form tag that is on the current html page. We then create a url based login string using the input element ‘names’ for both of the required login request parameters and the supplied user string and password parameters.

Generating passwords from keywords: 
Attempting to login with keywords extracted from web pages is very unlikely to be successful, however, performing various transformations on our password list greatly increases our chances of being a correct password. We broke each transformation down into a specific function. The transformations include: converting to leetspeak, uppercase, lowercase, and reversing the string. These functions can be found in the password_generator.py script.

leetspeak: Takes in a single password string and uses the python string transformation to case-insensitively map standard alphabetical characters to their numerical leetspeak equivalents.

reverse: Takes in a single password string and uses list comprehension, substring, and negative indexing to reverse the characters in the string.

uppercase: Takes in a single password string and uses the standard python string library function to convert all characters to uppercase.

lowercase: Takes in a single password string and uses the standard python string library function to convert all characters to lowercase.

generate_password_list: Takes in a master list of passwords (these are the keywords collected during the web crawl process) and for each passwords applies the four transformations (uppercase, lowercase, reverse, leetspeak) and adds these newly created passwords into a set. This removes the chance for duplicate passwords that will be used for form brute forcing.

Web crawling, command arguments and brute forcing: 
There are two strategies available for crawling, the first (and default) way of crawling is by performing an iterative breadth-first search with urls. The second way of crawling is by performing a recursive depth-first search with the urls. Due to the nature of the algorithms, bfs being FIFO (first in first out) and dfs being LIFO (last in first out) the order in which pages are parsed for keywords, links, and forms are typically different. In combination with a max page depth, and maximum page visited limit, there is a good possibility that the results of both the crawl and bruteforce will be different. Typically this won’t be the case as long as the maximum page visited limit is high enough.

There are five optional command line arguments that the web crawler takes in and one required argument, the starting url. The optional arguments determine the login username, the max depth the crawl will reach, the max number of unique pages the web crawler will visit, the type of search algorithm to use, and the user agent to be used in the http requests. Since all the command args are optional, there are default values for each of them. We opted for this strategy for our command line arguments because it increases the flexibility of our program.

In order to fight against most website’s anti brute force measures (usually send a 500 - Internal Server Error - and block any login attempts we make to that form for a set amount of time), we opted to continuously make the same request until that undefined timer length has elapsed. This allows our web crawler to test every combination regardless of the defense the website has. The only downside to this is that it drastically increases the time taken for the full bruteforce process to finish.

web_crawler: Takes in flags for method of search, page depth, max page visited, and starting point. Using these flags it calls either bfs or dfs and sets the parameters for those functions accordingly. After the initial crawl is done, if the max page visited value has not been reached then each url from the website’s robots.txt file will be used as an entry point for the selected search. After the robots.txt crawl is finished, if the max page visited value has still not been reached then each subdomain is appended to the entry point taken from command line and a call to web crawl is initiated on the appended url. 

get_subdomains: Takes in a url as a parameter, calls the ‘read_subdomains’ function, extracts the host from the url, and removes the URL’s subdomain if there currently is one. We then check if the subdomain on the current URL is also in our list of possible subdomains. If it is, then we overwrite the host variable with the original host minus the subdomain that is currently appended to it. Finally, we generate a list of subdomain plus host combinations and return the list.

read_subdomains: Opens a file that’s name is stored in the constant ‘SUBDOMAINS_FILE_PATH’. This constant points to the ‘subdomains-100.txt’ which holds a hundred of the common subdomains used on the web. Each line read from the file is stripped of it’s newline character and returned as a list of possible subdomains to crawl.

crawl_subdomains: Takes in a search mode, a http header as a python dictionary, a global counter object, a set of urls with login forms, a set of keywords, and a set of seen urls. For each of the subdomains, we create a socket connection, and reformat the url. Then depending on the method of search, we call the search function with a starting url of the formatted url (subdomain + url). If there is a an error during the bfs or creating the connection, we catch it and print a helpful error message. Finally, we close the connection.

crawl_robots: Takes in a search mode, a http header as a python dictionary, a global counter object, a set of urls with login forms, a set of keywords, and a set of seen urls. We then determine the status of the url, and how (if at all) the string ‘robots.txt’ should be appended to the end of the url. Then we make a get request to the url where robots.txt is located. We take the resulting string from the text file and split it by new line characters, then we filter out all the paths in both ‘Disallow: path’ and ‘Allow: path’ parts of robots.txt. We further parse the string by splitting every list entry by a space character. Once we have each path we combine the url taken in as a parameter and the path from robots.txt and create a list of new urls to crawl. For each of the created links we call a search function with the starting url as one of the created links. If any errors are thrown during any of the crawling or requests, we catch the error and print a helpful message.

_crawl_dfs:  This is the private dfs (depth-first search) function. The parameters are a starting url to crawl, a node containing the current depth and url, http header attributes as a Python dictionary, the set structures for visited urls, keywords, and urls with forms. We use a python lambda function to recursively call ‘_crawl_dfs’ with the same set structures, and header dictionary with new start_url, node with new url and incremented depth counter. We then call the process node function to extract all the usable data from the current web page, and to make the next call dfs function call.  

crawl_dfs: This is the public function entry point for initiating the DFS (depth-first search) web crawling strategy. In this function we take in key data structures as parameters that collect our data during the search such as: keywords, and  urls with login forms as well as vital structures needed for a dfs like the ‘seen’ set to keep track of previously visited pages. Most importantly, this function makes the initial call to the private recursive ‘_crawl_dfs’ function. After the crawl is finished (the recursive function returns).
crawl_bfs: Takes in a starting_url, and http header attributes as a python dictionary, a set of seen urls, a set of keywords found, and a set of urls with login forms. We exclusively use the set structure for form_urls, keywords, and our collection of seen urls. Using a set for these collections removes the possibility for duplicate entries. For the queue used to guide the bfs algorithm we opted to use python’s collections library data structure deque which is referred to as a ‘high performance container data type’. These small optimizations with deque and non-duplicated entries allow us to crawl pages more efficiently which helps the crawler scale better. Then we perform a the bfs algorithm. We utilize a python lambda expression to add the newly found urls from the ‘process_node’ function to our queue. We repeat this process until our queue is empty.

process_node: This function handles: making the get request, initializing the HTML_Parser, and finding the forms, links, and keywords. It takes in a starting url, a node object containing a url and a depth counter, http header attributes as a python dictionary, set data structures for urls with login forms, keywords, and already visited urls. It also takes in the lambda function for adding child urls to the bfs queue and dfs stack. First we send a GET request to the starting_url parameter, then we initialize the HTMLParser on the web page returned from the GET request. Using the html parser we call ‘extract_words’ to find and add new keywords to our keywords set, then we use ‘detect_login_form’ to test whether or not the current page contains a login form, if it does we add the current url into the forms set. Next we check whether or not the current node’s depth counter exceeds the max depth set by the user, if it does not we extract the urls on the current web page, reformat them. If we haven't seen them before add them to the set of seen pages and then add the url to the end of our queue or stack for bfs or dfs respectively. To make sure we don’t visit the same page twice, we use the ‘add_duplicate_url’ function. 

add_duplicate_url: Takes in a url and the Python set data structure containing all the already visited urls that the crawler navigated during it’s crawl. If the URL taken in as a parameter has a trailing slash then we also want to add a url to the set that doesn’t contain the trailing slash, however, if the url parameter is missing the trailing slash we want to add a url to our set that has the trailing slash. This is an important function because a url with or without a trailing slash will lead to the same web page, but having both versions in our seen set removes the possibility for crawling the same page more than once.

brute_force: Takes in a username, a user agent string, a list of keywords, and  urls with forms on the page. We start by generating our modified passwords (this roughly adds 4 * n more passwords for a list of n passwords). Then for each url containing a form, we create a get request header using our user agent string, and perform a get request. We initialize a HTMLParser for the html page from the get request. Then for every password in our list, we create a login string that can be used for that specific login form, we create the post request using our user agent, the content-type and the content-length. We send the post request to the url and capture the response. If the status of the response is a 5XX, we continuously try logging in until we get a 302 (a successful login) or any other status code (this is a failure).
	
Url helpers:
With modularity and clean code in mind, the url_utils provides us with various url parsing and modification functions. They are used throughout the web crawling process. Although most functions are simplistic in nature, there are many edges cases that we had to be aware of and account for, particularly in the ‘extract_url_parts’ and ‘reformat_url’ functions.

add_protocol: Takes in a url and a port as parameters, if port parameter is 80 and the current url doesn’t start with the substring for standard http, we prepend the http string to the url. If the port number is 443, indicating https (http with an ssl wrapper), and the current url doesn’t start with the substring for standard https, we prepend the string to the url. This ensures that every link we attempt to crawl has the a http or https indicator that matches the port number we are attempting to make the request with.

extract_url_parts: Takes in a URL string as a parameter, by defaults the port is set to the http protocol (port 80) and the path is set to an empty string. First we determine the proper port number, we split the url by the substring ‘://’, this leaves us with the remaining url (ex: www.google.com) and the protocol string (ex: http or https). If the protocol is https we want to change the default value for the port from 80 to 443 (the port for https). Next we want to split the host (ex: www.google.com) from the path (ex: /search?id=1234). We set the host value and then check if there is a valid path, if there is we also set the path. Finally, we have to check if there is a port number that the host specifies, we check this by checking for the existence of a ‘:’ character in the host string. If we find one then we set the host string to the substring before the ‘:’ and attempt to set the port number to whatever substring follows the ‘:’. We then return the final host, path, and port that we parsed from the url parameter. 

reformat_url: Takes in a url and base url as a string. If a base url is provided then we want to prepend the base url to the url parameter. We perform a check to make sure that the url is not based on a relative path containing a #, if it is we’ll ignore it. Else, we remove the trailing slash from the url it it exists, then we look if the url contains the substring (‘//’ or ‘./) at the start of the string. If a ‘//’ is found, we add the appropriate protocol to the url. If a ‘./’ is found then we remove that substring from the url (relative url). If instead we find the substring ‘/’ at the start, we want to remove it from the start of the url string. Finally, if the base_url doesn’t contain the url string we want to prepend the base_url + ‘/’ to the url string then we return the url. If the base url is not provided then we want to extract the port number from the url using the ‘extract_url_parts’ function, add the proper protocol string with the ‘add_protocol’ function and then return the modified url string.


High-level web crawling and brute forcing overview:
Setup:
Program is ran with command line arguments for: type of search algorithm, max page count, max depth count, username/email for login and a user agent. The search algorithm is called, ‘crawl_bfs’ or ‘crawl_dfs’ for bfs and dfs respectively.
The chosen algorithm makes an initial GET request to the entry point url, initializes the required data structures.
Initial search:
Each page is visited, it is scraped for keywords, links, and login forms using BeautifulSoup and NLTK together. The keywords, links, and login forms are checked for duplicate entries and then added to to sets for use later.
After extracting the data, the links found on the page have their current depth calculated to make sure that the max depth is not exceeded, then the urls are modified is necessary and added to the queue or stack used by the bfs or dfs we’re running.
Subdomain search:
After the initial search, we read in all likely subdomains from our subdomains-100.txt file.
We then create new urls for each of the subdomains found in the file, and we add the unique ones to to a list of new urls to crawl.
For each of the unique links we call a bfs or dfs (depending on which search algorithm was chosen) with an entry point of the unique link.
Robots.txt search:
After the subdomain search, we read in all the additional paths the website contains in it’s robots.txt file. 
We add the unique urls to a list, and modify them if required.
Then we call a bfs or dfs on each of those newly created urls.
Password generation:
We pass the list of unique passwords into the password generator and create a max of 4 additional passwords for each password in our starting list.
Form bruteforce:
For each of the urls we get the html page, and find which input values are needed to attempt a login.
Using the command line argument for username/email, the name/ids for the input fields and every single password in our list of password we create a new login string for every combination.
Then for each of the urls we make a post request for each of the login strings for that particular url.
We listen for the POST request’s response status code, if successful we print the url, the login string, and a success message, if unsuccessful we move onto the next login string.

Setup Instructions:
Command line arguments:
	Optional arguments:
	-url value: an integer, description: URL, required: yes
	--username value: a string, description: Username, default: admin
	--maxdepth value: an integer, description: max depth to reach while crawling, default: 10
	--maxpages value: an integer, description: max amount of unique pages to visit, default: 10
	--mode value: a string, description: the algorithm to crawl with, either bfs or dfs, default: bfs
	--useragent value: a string, description: User agent for making requests, default: to be determined by the network request

For help with commands, both --help and -h are available
An example run would look like the following: python main.py -url some_url --u admin --maxdepth 10 --maxpages 10 --mode bfs --useragent some_user_agent

Dependencies:
	Python 3.X
	BeautifulSoup
	NLTK (Natural Language Toolkit)
	** Both BeautifulSoup and NLTK can be installed via pip **

Distribution of work:
	Brandon Chen - requests.py, html_parser.py, url_utils.py, subdomains crawling, bfs/dfs, form bruteforcing 
Hong Jie Cen - creating a website, dfs, part of password bruteforcing, powerpoint
Nicholas Pirrello - password generation, report document, bfs, robots.txt
Seokhoon Kim - crawl_dfs, brute-forcing, command-arg parsing, password_generator

References and online examples:
Python Sockets:
Language Docs:
https://docs.python.org/3/library/socket.html
Stack Overflow: 
https://stackoverflow.com/questions/14140914/how-to-use-socket-fetch-webpage-use-python
https://stackoverflow.com/questions/50243235/send-data-through-post-request
	BeautifulSoup:
		Library Docs:
		https://www.crummy.com/software/BeautifulSoup/bs4/doc/

	NLTK (Natural Language Toolkit):
		Library Docs:
		https://www.nltk.org/api/nltk.html
	
Additional comments:
	



