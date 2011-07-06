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
#           'filename': <filename of image (string)>
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
#   if image_details != None:
#       print image_details['url']
#       print image_details['filename']
#       print str(image_details['size'])
#       if image_details['width'] != None:
#           print str(image_details['width'])
#       if image_details['height'] != None:
#           print str(image_details['height'])
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
import os

class HeadRequest(urllib2.Request):
    def get_method(self):
        return "HEAD"
        
class StarImage():
    
    def __init__(self, url_or_html, base_url=None):
        self.url_or_html = url_or_html
        self.base_url = base_url
        
    @staticmethod 
    def is_url(url):
        if url == None:
            return False
        else:
            parts = urlparse.urlparse(url)
            return parts.scheme in ['http', 'https']
    
    @staticmethod
    def is_html(html):
        if html == None:
            return False
        else:
            return re.search('<html.*?>', html, re.I|re.S) != None 
            
    @staticmethod
    def is_number(s):
        if s == None:
            return False
        else:
            try:
                float(s)
                return True
            except ValueError:
                return False 
                
    @staticmethod            
    def get_url_content_length(url):
        content_length = 0;
        try:
            response = urllib2.urlopen(HeadRequest(url))
        except urllib2.URLError, e:
            if hasattr(e, 'reason'):
                StarImage.handle_exception('We failed to read a server for: ' + url + '. Reason: ' + str(e.reason))
            elif hasattr(e, 'code'):
                StarImage.handle_exception('The server couldn\'t fulfill the request for: ' + url + '. Error code: ' + str(e.code))
        else:
            if response.headers.has_key('content-length'):
                content_length = long(response.headers['content-length'])
        return content_length                           
    
    @classmethod
    def handle_exception(cls, message):
         logging.error('starimage: ' + message)   
     
    def __get_doc_from_url(self):
        doc = None
        try:
            doc = lxml.html.fromstring(urllib2.urlopen(self.url_or_html).read())  
        except IOError, e:
            StarImage.handle_exception('Error opening url: ' + self.url_or_html)
        return doc
        
    def __get_doc(self):
        doc = None
        from_url = False
        try:
            if self.url_or_html == None:
                doc = None
            elif StarImage.is_url(self.url_or_html):
                doc = self.__get_doc_from_url()
                from_url = True
            elif StarImage.is_html(self.url_or_html):
                doc = lxml.html.document_fromstring(self.url_or_html)
            else:
                doc = lxml.html.fragment_fromstring(self.url_or_html)
        except lxml.etree.ParserError, e:
            StarImage.handle_exception('Error parsing HTML')
        else:    
            if doc != None:
                if self.base_url == None and from_url == True:            
                    parts = urlparse.urlparse(self.url_or_html)
                    if parts.scheme in ['http', 'https'] and parts.hostname != None:
                        self.base_url = parts.scheme + '://' + parts.hostname
                if self.base_url != None:
                    doc.make_links_absolute(self.base_url)        
        return doc                                     
           
    def __get_images(self, doc):
        if doc == None:
            return None
        else:
            return doc.xpath('//img')    

    def __get_image_details(self, images):
        image_details = []
        if images != None:
            for image in images:            
                src = image.get('src')
                if StarImage.is_url(src):
                    url_already_used = False
                    for image_item in image_details:
                        if image_item['url'] == src:
                            url_already_used = True
                            break
                    if not url_already_used:
                        image_detail = {'url': src, 'width': None, 'height': None}
                        image_width = image.get('width')
                        image_height = image.get('height')
                        if StarImage.is_number(image_width):
                            image_detail['width'] = int(image_width)
                        if StarImage.is_number(image_height):
                            image_detail['height'] = int(image_height)
                        image_details.append(image_detail)
        return image_details        

    def __get_largest_image(self, images): 
        largest_details = None   
        image_details = self.__get_image_details(images)
        if len(image_details) > 0:
            content_length = 0
            for image_detail in image_details:
                content_length = StarImage.get_url_content_length(image_detail['url'])  
                if largest_details == None:
                    largest_details = {'url': None, 'size': None}
                if largest_details['size'] == None or content_length > largest_details['size']:
                    largest_details['url'] = image_detail['url']
                    largest_details['size'] = content_length
                    largest_details['width'] = image_detail['width']
                    largest_details['height'] = image_detail['height']
        if largest_details != None:
            largest_details['filename'] = os.path.basename(largest_details['url'])
        return largest_details  

    def extract(self):
        doc = self.__get_doc()
        if doc == None:
            return None
        else:
            images = self.__get_images(doc)
            return self.__get_largest_image(images)
            
def extract(url_or_html, base_url=None):
    star = StarImage(url_or_html, base_url)
    return star.extract()