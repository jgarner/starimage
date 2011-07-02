import starimage
import unittest

class TestStarImage(unittest.TestCase):
    
    def test_interface(self):
        self.assertTrue(starimage.extract != None)
        self.assertTrue(starimage.is_url != None)
        self.assertTrue(starimage.is_html != None)
        self.assertTrue(starimage.get_html_from_url != None)
        self.assertTrue(starimage.get_all_images_from_html != None)
        self.assertTrue(starimage.get_largest_image != None)
        self.assertTrue(starimage.get_image_content_length != None)
        
    def test_is_url_false_if_url_equals_none(self):
        self.assertFalse(starimage.is_url(None))
        
    def test_is_url_false_if_not_http_or_https(self):
        self.assertFalse(starimage.is_url('ftp://example'))
    
    def test_is_url_true_if_http(self):
        self.assertTrue(starimage.is_url('http://example.com')) 
        
    def test_is_url_true_if_https(self):
        self.assertTrue(starimage.is_url('https://example.com'))           
        
    def test_is_html_false_if_equals_none(self):
        self.assertFalse(starimage.is_html(None))  
        
    def test_is_html_false_if_no_html_tag_found(self):
        self.assertFalse(starimage.is_html("sfsf<img>"))
        
    def test_is_html_true_if_html_tag_found(self):
        self.assertTrue(starimage.is_html('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"><html>'))        
        
    def test_is_html_true_if_html_tag_found_with_attributes(self):
        self.assertTrue(starimage.is_html('<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">'))        
        
if __name__ == '__main__':
    unittest.main()

