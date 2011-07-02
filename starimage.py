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
    
def get_html_from_url():
    return True
    
def get_all_images_from_html():
    return True
    
def get_largest_image():
    return True
    
def get_image_content_length():
    return True