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
        
if __name__ == '__main__':
    unittest.main()

