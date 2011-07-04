import logging
import urlparse
import re
import lxml.html
            
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
  
def handle_exception(message):
     logging.error('starimage: ' + message)
             
def get_doc_from_url(url):
    doc = None
    try:
       doc = lxml.html.parse(url).getroot()   
    except IOError, e:
        handle_exception('Error opening url: ' + url)
    return None
              
def get_doc(url_or_html, base_url=None):
    doc = None
    from_url = False
    try:
        if url_or_html == None:
            doc = None
        elif is_url(url_or_html):
            doc = get_doc_from_url(url_or_html)
            from_url = True
        elif is_html(url_or_html):
            doc = lxml.html.document_fromstring(url_or_html)
        else:
            doc = lxml.html.fragment_fromstring(url_or_html)
    except lxml.etree.ParserError, e:
        handle_exception('Error parsing HTML')
    else:    
        if doc != None:
            if base_url == None and from_url == True:            
                parts = urlparse.urlparse(url_or_html)
                if parts.scheme in ['http', 'https'] and parts.hostname != None:
                    base_url = parts.scheme + '://' + parts.hostname
            if base_url != None:
                doc.make_links_absolute(base_url)        
    return doc
                    
def get_images(doc):
    if doc == None:
        return None
    else:
        return doc.xpath('//img')
    
def get_image_urls(images):
    image_urls = []
    if images != None:
        for image in images:
            src = image.get('src')
            if is_url(src):
                image_urls.append(src)
        image_urls = set(image_urls)
    return image_urls
                
def get_largest_image():
    return True
    
def get_image_content_length():
    return True   
     
def extract(url_or_html):
    return True     