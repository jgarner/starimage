# Use starimage to find details of the largest image on a web page.
# 
# Main usage:
# 
# starimage.extract(url_or_html, base_url=None)
# 
#     Params:
#       url_or_html:
#           can be a full url eg 'http://www.example.com' (must be http or https)
#           can be an html string or html fragment.
# 
#       base_url: (optional)
#           starimage can only get the size of an image if it is an absolute path.
#           Relative paths don't work. If base_url is set relative image urls will
#           will use base_url as its base. If url_or_html param is a url the base_url
#           will automatically be generated from the url but if base_url is set this
#           will be used first.
# 
#     Returns:
#       If no image is found None is returned
#       otherwise a dictionary object is returned
#       {
#           'url': <url of largest image found (string)>,
#           'size': <size in bytes of image (long)>,
#           'width': <None or width of image if width attribute set in <img /> tag (int)>,
#           'height': <None or height of image if height attribute set in <img /> tag (int)>
#       }
# 
# Example:
#   image_details = starimage.extract('http://www.example.com')
#
#   html = "<html><head></head><body>\n\
#       <img src='http://a.com/img.gif' />\n\
#       <img src='http://a.com/img.jpg' />\n\
#       </body></html>"
#   image_details = starimage.extract(html)
#
#   fragment = "<div><img src='http://a.com/img1.gif' />\n\
#       img src='http://a.com/img.jpg' /></div>"
#   image_details = starimage.extract(fragment)
#
#   print image_details['url']
#   print image_details['size']
#   print image_details['width']
#   print image_details['height']
# 
# Library dependencies:
#   lxml: http://lxml.de/
# 
# author: Joshua Garner

import logging
import urlparse
import re
import lxml.html
import urllib2    
            
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
    return doc
              
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
    
def is_number(s):
    if s == None:
        return None
    else:
        try:
            float(s)
            return True
        except ValueError:
            return False
        
def get_image_details(images):
    image_details = []
    if images != None:
        for image in images:            
            src = image.get('src')
            if is_url(src):
                url_already_used = False
                for image_item in image_details:
                    if image_item['url'] == src:
                        url_already_used = True
                        break
                if not url_already_used:
                    image_detail = {'url': src, 'width': None, 'height': None}
                    image_width = image.get('width')
                    image_height = image.get('height')
                    if is_number(image_width):
                        image_detail['width'] = int(image_width)
                    if is_number(image_height):
                        image_detail['height'] = int(image_height)
                    image_details.append(image_detail)
    return image_details        
              
class HeadRequest(urllib2.Request):
    def get_method(self):
        return "HEAD"
                            
def get_url_content_length(url):
    content_length = 0;
    try:
        response = urllib2.urlopen(HeadRequest(url))
    except urllib2.URLError, e:
        if hasattr(e, 'reason'):
            handle_exception('We failed to read a server for: ' + url + '. Reason: ' + str(e.reason))
        elif hasattr(e, 'code'):
            handle_exception('The server couldn\'t fulfill the request for: ' + url + '. Error code: ' + str(e.code))
    else:
        if response.headers.has_key('content-length'):
            content_length = long(response.headers['content-length'])
    return content_length
    
def get_largest_image(images): 
    largest_details = None   
    image_details = get_image_details(images)
    if len(image_details) > 0:
        content_length = 0
        for image_detail in image_details:
            content_length = get_url_content_length(image_detail['url'])           
            if largest_details == None:
                largest_details = {'url': None, 'size': None}
            if largest_details['size'] == None or content_length > largest_details['size']:
                largest_details['url'] = image_detail['url']
                largest_details['size'] = content_length
                largest_details['width'] = image_detail['width']
                largest_details['height'] = image_detail['height']
    return largest_details  
    
def extract(url_or_html, base_url=None):
    doc = get_doc(url_or_html, base_url)
    if doc == None:
        return None
    else:
        images = get_images(doc)
        return get_largest_image(images)