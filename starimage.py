import logging
import urlparse
import re
import lxml.html

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
        return re.search('<html.*?>', html, re.I|re.S) != None   
    
def get_doc(url_or_html):
    try:
        if url_or_html == None:
            return None
        elif is_url(url_or_html):
            return lxml.html.parse(url_or_html)
        elif is_html(url_or_html):
            return lxml.html.document_fromstring(url_or_html)
        else:
            return lxml.html.fragment_fromstring(url_or_html)
    except IOError, e:
        handle_exception('Error opening url: ' + url_or_html)
    except lxml.etree.ParserError, e:
        handle_exception('Error parsing HTML')
                    
def get_images(doc):
    if doc == None:
        return None
    else:
        return doc.xpath('//img')
    
def get_largest_image():
    return True
    
def get_image_content_length():
    return True

def handle_exception(message):
     logging.error('starimage: ' + message)