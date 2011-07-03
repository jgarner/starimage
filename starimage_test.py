import starimage
import lxml
import mock
from mock import patch
import unittest

class TestStarImage(unittest.TestCase):
    
    def test_interface(self):
        self.assertIsNotNone(starimage.extract)        
        self.assertIsNotNone(starimage.is_url)
        self.assertIsNotNone(starimage.is_html)
        self.assertIsNotNone(starimage.get_doc)
        self.assertIsNotNone(starimage.get_images)
        self.assertIsNotNone(starimage.get_largest_image)
        self.assertIsNotNone(starimage.get_image_content_length)
        self.assertIsNotNone(starimage.handle_exception)
       
    # test is_url    
    def test_is_url_return_false_if_url_equals_none(self):
        self.assertFalse(starimage.is_url(None))
        
    def test_is_url_return_false_if_not_http_or_https(self):
        self.assertFalse(starimage.is_url('ftp://example'))
    
    def test_is_url_return_true_if_http(self):
        self.assertTrue(starimage.is_url('http://example.com')) 
        
    def test_is_url_return_true_if_https(self):
        self.assertTrue(starimage.is_url('https://example.com'))           
        
    # test is_html    
    def test_is_html_return_false_if_equals_none(self):
        self.assertFalse(starimage.is_html(None))  
        
    def test_is_html_return_false_if_no_html_tag_found(self):
        self.assertFalse(starimage.is_html("sfsf<img>"))
        
    def test_is_html_return_true_if_html_tag_found(self):
        self.assertTrue(starimage.is_html('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"><html>'))        
        
    def test_is_html_return_true_if_html_tag_found_with_attributes(self):
        self.assertTrue(starimage.is_html('<HTML xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">'))        
        
    # test get_doc
    def test_get_doc_return_none_if_param_is_none(self):
        self.assertIsNone(starimage.get_doc(None))

    @patch('lxml.html.parse')
    def test_get_doc_raises_ioerror_with_invalid_url(self, parse_mock):
        parse_mock.side_effect = IOError()
        self.assertRaises(IOError, starimage.get_doc('http://1234abcdef.co.nz.au'))
        
    @patch('lxml.html.parse')    
    def test_get_doc_returns_instance_of_element_tree_with_valid_url(self, parse_mock):
        parse_mock.return_value = lxml.etree._ElementTree()
        self.assertIsInstance(starimage.get_doc('http://www.google.co.nz'), lxml.etree._ElementTree)        
        
    def test_get_doc_raises_parsererror_with_empty_string(self):
        self.assertRaises(lxml.etree.ParserError, starimage.get_doc(''))    
        
    def test_get_doc_returns_none_with_empty_string(self):
        self.assertIsNone(starimage.get_doc('')) 
        
    def test_get_doc_returns_instance_of_element_with_valid_html(self):
        self.assertIsInstance(starimage.get_doc('<html><head></head><body><div>Hi</div></body></html>'), lxml.etree._Element)   
        
    def test_get_doc_returns_instance_of_element_with_valid_html_fragment(self):
        self.assertIsInstance(starimage.get_doc('<div>Hi</div>'), lxml.etree._Element)  
    
    # test get_images   
    def test_get_images_return_none_if_doc_is_none(self):
        self.assertIsNone(starimage.get_images(None))                         
        
if __name__ == '__main__':
    unittest.main()

