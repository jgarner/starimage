import starimage
import lxml
import mock
from mock import Mock, patch
import urllib2
import unittest

class TestStarImage(unittest.TestCase):        
                     
    html = "<html><header></header><body>\n\
        <img src='/r1.gif' />\n\
        <img src='/r2.gif' />\n\
        <img src='/r3.gif' />\n\
        <img src='http://a.com/1.gif' />\n\
        <img src='http://a.com/2.gif' width='100', height='300' />\n\
        <img src='http://a.com/3.gif' />\n\
        <img src='http://a.com/4.gif' />\n\
        </body></html>"
            
    def get_content_length(*args, **kwargs):
        url  = args[1]
        if url == 'http://a.com/1.gif':
            return 100
        elif url == 'http://a.com/2.gif':
            return 500
        elif url == 'http://a.com/3.gif':
            return 300
        elif url == 'http://a.com/4.gif':
            return 450
        else:
            return 0 
                                   
    def test_interface(self):                    
        self.assertIsNotNone(starimage.is_url)
        self.assertIsNotNone(starimage.is_html)
        self.assertIsNotNone(starimage.handle_exception)
        self.assertIsNotNone(starimage.get_doc_from_url)
        self.assertIsNotNone(starimage.get_doc)
        self.assertIsNotNone(starimage.get_images)
        self.assertIsNotNone(starimage.get_image_details)
        self.assertIsNotNone(starimage.get_url_content_length)
        self.assertIsNotNone(starimage.get_largest_image)
        self.assertIsNotNone(starimage.extract)       
                            
# test is_url(url)
    def test_is_url_return_false_if_url_equals_none(self):
        self.assertFalse(starimage.is_url(None))
        
    def test_is_url_return_false_if_not_http_or_https(self):
        self.assertFalse(starimage.is_url('ftp://example'))
    
    def test_is_url_return_true_if_http(self):
        self.assertTrue(starimage.is_url('http://example.com')) 
        
    def test_is_url_return_true_if_https(self):
        self.assertTrue(starimage.is_url('https://example.com'))           
        
# test is_html(html) 
    def test_is_html_return_false_if_equals_none(self):
        self.assertFalse(starimage.is_html(None))  
        
    def test_is_html_return_false_if_no_html_tag_found(self):
        self.assertFalse(starimage.is_html("sfsf<img>"))
        
    def test_is_html_return_true_if_html_tag_found(self):
        self.assertTrue(starimage.is_html('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"><html>'))        
        
    def test_is_html_return_true_if_html_tag_found_with_attributes(self):
        self.assertTrue(starimage.is_html('<HTML xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">'))        
       
# test get_doc_from_url(url)
    @patch('lxml.html.parse')
    def test_get_doc_from_url_raises_ioerror_with_invalid_url(self, parse_mock):
        parse_mock.side_effect = IOError()
        self.assertRaises(IOError, starimage.get_doc_from_url('http://invalidurl.com'))    
                     
# test get_doc(url_or_html, base_url=None)
    def test_get_doc_return_none_if_param_is_none(self):
        self.assertIsNone(starimage.get_doc(None))
    
    @patch('starimage.get_doc_from_url')
    def test_get_doc_returns_none_with_invalid_url(self, get_doc_from_url_mock):
        get_doc_from_url_mock.return_value = None
        self.assertIsNone(starimage.get_doc('http://invalidurl.com'))
        
    @patch('starimage.get_doc_from_url')
    def test_get_doc_returns_element_with_valid_url(self, parse_mock):
        parse_mock.return_value = lxml.html.document_fromstring('<html></html>')
        self.assertIsInstance(starimage.get_doc('http://example.com'), lxml.etree._Element)               
        
    def test_get_doc_raises_parsererror_with_empty_string(self):
        self.assertRaises(lxml.etree.ParserError, starimage.get_doc(''))    
        
    def test_get_doc_returns_none_with_empty_string(self):
        self.assertIsNone(starimage.get_doc('')) 
        
    def test_get_doc_returns_instance_of_element_with_valid_html(self):
        self.assertIsInstance(starimage.get_doc('<html><html>'), lxml.etree._Element)   
        
    def test_get_doc_returns_instance_of_element_with_valid_html_fragment(self):
        self.assertIsInstance(starimage.get_doc('<div>Hi</div>'), lxml.etree._Element)  
        
    def test_get_doc_makes_imgs_absolute_with_base_url(self):
        doc = starimage.get_doc('<html><body><img src="/img1.gif" /></body></html>', 'http://example.com')
        imgs = doc.xpath('//img')
        self.assertEquals(imgs[0].get('src'), 'http://example.com/img1.gif')           
    
# test get_images(doc)
    def test_get_images_return_none_if_doc_is_none(self):
        self.assertIsNone(starimage.get_images(None))    
        
    def test_get_images_return_empty_list_if_doc_has_no_images(self):
        doc = starimage.get_doc('<html></html>')
        self.assertEquals(len(starimage.get_images(doc)), 0) 
                    
    def test_get_images_return_list_of_images_if_doc_has_images_from_html(self):
        doc = starimage.get_doc('<html><header></header><body><img src="/test.jpg" /><img src="/logo.gif" /></body></html>')
        imgs = starimage.get_images(doc)
        self.assertEquals(imgs[0].tag, 'img')                                 
    
# test get_image_details(images)
    def test_get_image_details_returns_empty_list_if_no_images(self):
        html = '<html><header></header><body></body></html>'
        doc = starimage.get_doc(html)
        imgs = starimage.get_images(doc)        
        image_details = starimage.get_image_details(imgs)
        self.assertEquals(len(image_details), 0)
        
    def test_get_image_details_returns_only_absolute_path_image_urls(self):
        html = '<html><header></header><body><img src="/relative.jpg" /><img src="http://example.com/logo.gif" /></body></html>'
        doc = starimage.get_doc(html)
        imgs = starimage.get_images(doc)        
        image_details = starimage.get_image_details(imgs)
        self.assertEquals(len(image_details), 1)
        self.assertEquals(image_details[0]['url'], 'http://example.com/logo.gif')
        
    def test_get_image_details_returns_only_unique_urls(self):
        html = '<html><header></header><body><img src="http://example.com/logo.gif" /><img src="http://example.com/logo.gif" /></body></html>'
        doc = starimage.get_doc(html)
        imgs = starimage.get_images(doc)        
        image_details = starimage.get_image_details(imgs)
        self.assertEquals(len(image_details), 1)

# test get_url_content_length(url)
    @patch('urllib2.urlopen')
    def test_get_url_content_length_returns_0_if_invalid_url(self, urlopen_mock):
        urlopen_mock.side_effect = urllib2.URLError('error')
        self.assertEquals(starimage.get_url_content_length('http://invalidurl.com'), 0) 
        
    @patch('urllib2.urlopen')
    def test_get_url_content_length_returns_content_length_from_header(self, urlopen_mock):
        my_mock = Mock()
        my_mock.headers = {'content-length': 100}
        urlopen_mock.return_value = my_mock
        self.assertEquals(starimage.get_url_content_length('http://invalidurl.com'), 100)             
                
# test_get_largest_image(images)
    def test_get_largest_image_returns_none_if_image_list_is_none(self):
        self.assertIsNone(starimage.get_largest_image(None)) 
        
    def test_get_largest_image_returns_none_on_empty_image_list(self):
        self.assertIsNone(starimage.get_largest_image([]))                    
    
    @patch('starimage.get_url_content_length')
    def test_get_largest_image_returns_largest_image_details(self, get_url_content_length_mock):
        get_url_content_length_mock.side_effect = self.get_content_length
        doc = starimage.get_doc(TestStarImage.html)
        imgs = starimage.get_images(doc)     
        details = starimage.get_largest_image(imgs)   
        self.assertEquals(details['url'], 'http://a.com/2.gif')
        self.assertEquals(details['size'], 500)
   
# test_extract(url_or_html, base_url=None)
    @patch('starimage.get_url_content_length')
    def test_extract_gets_largest_image(self, get_url_content_length_mock):
        get_url_content_length_mock.side_effect = self.get_content_length
        self.assertEquals(starimage.extract(TestStarImage.html)['url'], 'http://a.com/2.gif')
            
if __name__ == '__main__':
    unittest.main()