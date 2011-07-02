import urlparse
import re

def extract(url_or_html):
    return True
    
def is_url(url):
    if url == None:
        return False
    else:
        parts = urlparse.urlparse(url)
        return parts.scheme in ['http', 'https']
    
def is_html(html):
    if html == None:
        return False
    else:
        return re.search( '<html.*?>', html, re.I) != None
    
def parse_html_from_url():
    return True
    
def parse_html_from_string():
    return True    
    
def get_all_images():
    return True
    
def get_largest_image():
    return True
    
def get_image_content_length():
    return True