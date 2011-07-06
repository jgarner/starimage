# TESTING:
#
# To run the main tests please run this file:
#   python starimage_test.py
#   Note: This runs mocks only for all web requests.
# 
# You can run your own tests based on real web requests by using a few methods.
#
# Method to test html from a file:
#   starimage_test.test_html_from_file(file_path, expected_details, base_url=None):
#
#   Params:
#       file_path: full path to a file
#       expected_details: dictionary object of expected return results
#       base_url: base_url to use for relative urls (optional)
#
# Method to test from a full url or html string:
#   starimage_test.test_from_url_or_html(url_or_html, expected_details, base_url=None):
#
#   Params:
#       url_or_html: full url or html string
#       expected_details: dictionary object of expected return results
#       base_url: base_url to use for relative urls (optional)
#
# What is tested?
#   The first test is to make sure some details are returned.
#   If no details are returned an exception will be raised.
#
#   With each of the methods there is a param for a dictionary object for details you expect 
#   to be returned. You don't have to provide all the details only the ones you wish to test.
#   The expected details will be tested against the details returned and if an
#   expected detail doesn't match a returned detail an exception will be raised.
#
#       expected_details param example:
#           {
#               'url': (string),
#               'filename': (string),
#               'size': (long),
#               'width': (int),
#               'height': (int),
#           }
#
# Author: Joshua Garner

import starimage
from starimage import StarImage
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
    
    def setUp(self):
        self.star = StarImage('<html></html>')
        
    def tearDown(self):
      self.star = None
                    
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
    
    def test_starimage_is_an_instance_of_StarImage(self):
        self.assertIsInstance(self.star, starimage.StarImage)
        
    def test_staticmethods_interface(self):                    
        self.assertIsNotNone(starimage.StarImage.is_url)     
        self.assertIsNotNone(starimage.StarImage.is_html)
        self.assertIsNotNone(starimage.StarImage.is_number)
        self.assertIsNotNone(starimage.StarImage.get_url_content_length)
        
    def test_classmethods_interface(self):                    
        self.assertIsNotNone(starimage.StarImage.handle_exception)
        
    def test_private_functions_interface(self):                    
        self.assertIsNotNone(self.star._StarImage__get_doc_from_url)  
        self.assertIsNotNone(self.star._StarImage__get_doc) 
        self.assertIsNotNone(self.star._StarImage__get_images)
        self.assertIsNotNone(self.star._StarImage__get_image_details)     
        self.assertIsNotNone(self.star._StarImage__get_largest_image)        
        
    def test_public_functions_interface(self):                    
        self.assertIsNotNone(self.star.extract)  
            
    # test StarImage.is_url(url)
    def test_is_url_return_false_if_url_equals_none(self):
        self.assertFalse(starimage.StarImage.is_url(None))

    def test_is_url_return_false_if_not_http_or_https(self):
        self.assertFalse(starimage.StarImage.is_url('ftp://example'))

    def test_is_url_return_true_if_http(self):
        self.assertTrue(starimage.StarImage.is_url('http://example.com')) 

    def test_is_url_return_true_if_https(self):
        self.assertTrue(starimage.StarImage.is_url('https://example.com'))     
               
    # test StarImage.is_html(html) 
    def test_is_html_return_false_if_equals_none(self):
        self.assertFalse(starimage.StarImage.is_html(None))  

    def test_is_html_return_false_if_no_html_tag_found(self):
        self.assertFalse(starimage.StarImage.is_html("sfsf<img>"))

    def test_is_html_return_true_if_html_tag_found(self):
        self.assertTrue(starimage.StarImage.is_html('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"><html>'))        

    def test_is_html_return_true_if_html_tag_found_with_attributes(self):
        self.assertTrue(starimage.StarImage.is_html('<HTML xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">'))
                           
    # test StarImage.is_number(s)
    def test_is_number_returns_false_if_not_a_number(self):
        self.assertFalse(starimage.StarImage.is_number(None))
        self.assertFalse(starimage.StarImage.is_number("abcd"))
        self.assertFalse(starimage.StarImage.is_number("1a"))

    def test_is_number_returns_true_if_is_a_number(self):
        self.assertTrue(starimage.StarImage.is_number("1.12"))
        self.assertTrue(starimage.StarImage.is_number("85"))
                                    
    # test StarImage.get_url_content_length(url)
    @patch('urllib2.urlopen')
    def test_get_url_content_length_returns_0_if_invalid_url(self, urlopen_mock):
        urlopen_mock.side_effect = urllib2.URLError('error')
        self.assertEquals(starimage.StarImage.get_url_content_length('http://invalidurl.com'), 0) 

    @patch('urllib2.urlopen')
    def test_get_url_content_length_returns_content_length_from_header(self, urlopen_mock):
        my_mock = Mock()
        my_mock.headers = {'content-length': 100}
        urlopen_mock.return_value = my_mock
        self.assertEquals(starimage.StarImage.get_url_content_length('http://invalidurl.com'), 100)                                    
                                       
    # test StarImage.__get_doc_from_url(self, url)
    @patch('urllib2.urlopen')
    def test_get_doc_from_url_raises_ioerror_with_invalid_url(self, parse_mock):
        parse_mock.side_effect = urllib2.URLError('error')
        self.star.url_or_html = 'http://invalidurl.com'
        self.assertRaises(urllib2.URLError, self.star._StarImage__get_doc_from_url())
                                 
    # test StarImage.__get_doc(self, url_or_html, base_url=None)
    def test_get_doc_return_none_if_param_is_none(self):
        self.star.url_or_html = None
        self.assertIsNone(self.star._StarImage__get_doc())

    @patch.object(starimage.StarImage, '_StarImage__get_doc_from_url')
    def test_get_doc_returns_none_with_invalid_url(self, get_doc_from_url_mock):
        get_doc_from_url_mock.return_value = None
        self.star.url_or_html = 'http://invalidurl.com'
        self.assertIsNone(self.star._StarImage__get_doc())

    @patch.object(starimage.StarImage, '_StarImage__get_doc_from_url')
    def test_get_doc_returns_element_with_valid_url(self, parse_mock):
        parse_mock.return_value = lxml.html.document_fromstring('<html></html>')
        self.star.url_or_html = 'http://example.com'
        self.assertIsInstance(self.star._StarImage__get_doc(), lxml.etree._Element)               

    def test_get_doc_raises_parsererror_with_empty_string(self):
        self.star.url_or_html = ''
        self.assertRaises(lxml.etree.ParserError, self.star._StarImage__get_doc())    

    def test_get_doc_returns_none_with_empty_string(self):
        self.star.url_or_html = ''
        self.assertIsNone(self.star._StarImage__get_doc()) 

    def test_get_doc_returns_instance_of_element_with_valid_html(self):
        self.star.url_or_html = '<html><html>'
        self.assertIsInstance(self.star._StarImage__get_doc(), lxml.etree._Element)   

    def test_get_doc_returns_instance_of_element_with_valid_html_fragment(self):
        self.star.url_or_html = '<div>Hi</div>'
        self.assertIsInstance(self.star._StarImage__get_doc(), lxml.etree._Element)  

    def test_get_doc_makes_imgs_absolute_with_base_url(self):
        self.star.url_or_html = '<html><body><img src="/img1.gif" /></body></html>'
        self.star.base_url = 'http://example.com'
        doc = self.star._StarImage__get_doc()
        imgs = doc.xpath('//img')
        self.assertEquals(imgs[0].get('src'), 'http://example.com/img1.gif')
        
    # test StarImage.__get_images(doc)
    def test_get_images_return_none_if_doc_is_none(self):
        self.assertIsNone(self.star._StarImage__get_images(None))    

    def test_get_images_return_empty_list_if_doc_has_no_images(self):
        self.star.url_or_html = '<html></html>'
        doc = self.star._StarImage__get_doc()
        self.assertEquals(len(self.star._StarImage__get_images(doc)), 0) 
    
    def test_get_images_return_list_of_images_if_doc_has_images_from_html(self):
        self.star.url_or_html = '<html><header></header><body><img src="/test.jpg" /><img src="/logo.gif" /></body></html>'
        doc = self.star._StarImage__get_doc()
        imgs = self.star._StarImage__get_images(doc)
        self.assertEquals(imgs[0].tag, 'img')               
    
    # test StarImage.__get_image_details(images)
    def test_get_image_details_returns_empty_list_if_no_images(self):
        self.star.url_or_html = '<html><header></header><body></body></html>'
        doc = self.star._StarImage__get_doc()
        imgs = self.star._StarImage__get_images(doc)        
        image_details = self.star._StarImage__get_image_details(imgs)
        self.assertEquals(len(image_details), 0)
    
    def test_get_image_details_returns_only_absolute_path_image_urls(self):
          self.star.url_or_html = '<html><header></header><body><img src="/relative.jpg" /><img src="http://example.com/logo.gif" /></body></html>'
          doc = self.star._StarImage__get_doc()
          imgs = self.star._StarImage__get_images(doc)        
          image_details = self.star._StarImage__get_image_details(imgs)
          self.assertEquals(len(image_details), 1)
          self.assertEquals(image_details[0]['url'], 'http://example.com/logo.gif')
      
    def test_get_image_details_returns_only_unique_urls(self):
        self.star.url_or_html = '<html><header></header><body><img src="http://example.com/logo.gif" /><img src="http://example.com/logo.gif" /></body></html>'
        doc = self.star._StarImage__get_doc()
        imgs = self.star._StarImage__get_images(doc)        
        image_details = self.star._StarImage__get_image_details(imgs)
        self.assertEquals(len(image_details), 1)

    def test_get_image_details_returns_details(self):
        self.star.url_or_html = '<html><header></header><body><img src="http://b.com/a.gif" width="200" height="300" /></body></html>'
        doc = self.star._StarImage__get_doc()
        imgs = self.star._StarImage__get_images(doc)        
        image_detail = self.star._StarImage__get_image_details(imgs)[0]
        self.assertEquals(image_detail['url'], 'http://b.com/a.gif') 
        self.assertEquals(image_detail['width'], 200)  
        self.assertEquals(image_detail['height'], 300)   
    
    def test_get_image_details_returns_none_for_width_and_height_if_not_set(self):
        self.star.url_or_html = '<html><header></header><body><img src="http://b.com/a.gif" /></body></html>'
        doc = self.star._StarImage__get_doc()
        imgs = self.star._StarImage__get_images(doc)        
        image_detail = self.star._StarImage__get_image_details(imgs)[0]
        self.assertEquals(image_detail['url'], 'http://b.com/a.gif') 
        self.assertEquals(image_detail['width'], None)  
        self.assertEquals(image_detail['height'], None)                       
    
    # test StarImage.__get_largest_image(images)
    def test_get_largest_image_returns_none_if_image_list_is_none(self):
        self.assertIsNone(self.star._StarImage__get_largest_image(None)) 
    
    def test_get_largest_image_returns_none_on_empty_image_list(self):
        self.assertIsNone(self.star._StarImage__get_largest_image([]))                    
    
    @patch.object(starimage.StarImage, 'get_url_content_length')
    def test_get_largest_image_returns_largest_image_details(self, get_url_content_length_mock):
        get_url_content_length_mock.side_effect = self.get_content_length
        self.star.url_or_html = TestStarImage.html
        doc = self.star._StarImage__get_doc()
        imgs = self.star._StarImage__get_images(doc)     
        details = self.star._StarImage__get_largest_image(imgs)   
        self.assertEquals(details['url'], 'http://a.com/2.gif')
        self.assertEquals(details['filename'], '2.gif')
        self.assertEquals(details['size'], 500)
        self.assertEquals(details['width'], 100)
        self.assertEquals(details['height'], 300)
    
    # test StarImage.extract(url_or_html, base_url=None)
    @patch.object(starimage.StarImage, 'get_url_content_length')
    def test_extract_gets_largest_image(self, get_url_content_length_mock):
        get_url_content_length_mock.side_effect = self.get_content_length
        self.star.url_or_html = TestStarImage.html
        self.assertEquals(self.star.extract()['url'], 'http://a.com/2.gif')
        
    # test extract(url_or_html, base_url=None)
    @patch.object(starimage.StarImage, 'get_url_content_length')
    def test_extract_gets_largest_image(self, get_url_content_length_mock):
        get_url_content_length_mock.side_effect = self.get_content_length
        self.assertEquals(starimage.extract(TestStarImage.html)['url'], 'http://a.com/2.gif')        
   
# Test class to enable users to test from:
#   - a file containing html
#   - a full url
#   - a string containing html
class TestUserStarImage(unittest.TestCase):    
    def set_values(self, test_type, user_input, expected_details, base_url=None):
        self.test_type = test_type
        self.user_input = user_input
        self.expected_details = expected_details
        self.base_url = base_url
        
    def runTest(self):
        details = None
        if self.test_type == 1:
            details = starimage.extract(open(self.user_input).read(), self.base_url)
        else:
            details = starimage.extract(self.user_input, self.base_url)
        self.assertIsNotNone(details)
        if details != None:      
          if expected_details.has_key('url'):
            self.assertEquals(details['url'], expected_details['url'])
          if expected_details.has_key('filename'):
            self.assertEquals(details['filename'], expected_details['filename']) 
          if expected_details.has_key('size'):
            self.assertEquals(details['size'], expected_details['size'])
          if expected_details.has_key('width'):
            self.assertEquals(details['width'], expected_details['width']) 
          if expected_details.has_key('height'):
            self.assertEquals(details['height'], expected_details['height'])                                                      
     
# Wrapper for running a user based test on the TestUserStarImage class         
def run_user_test(test_type, file_path, expected_details, base_url=None): 
    test_case = TestUserStarImage()
    test_case.set_values(test_type, file_path, expected_details, base_url)
    suite = unittest.TestSuite()
    suite.addTest(test_case);
    unittest.TextTestRunner(verbosity=2).run(suite)  
    
# User test from a file path
def test_html_from_file(file_path, expected_details, base_url=None):
    run_user_test(1, file_path, expected_details, base_url)
    
# User test from a url or html
def test_from_url_or_html(url_or_html, expected_details, base_url=None):
    run_user_test(2, url_or_html, expected_details, base_url) 
        
if __name__ == '__main__':
     suite = unittest.TestLoader().loadTestsFromTestCase(TestStarImage)
     unittest.TextTestRunner(verbosity=2).run(suite)  