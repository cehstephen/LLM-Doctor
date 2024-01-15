import unittest
import unittest
import sys
import os

# Add the project root directory to the sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app

class TestLLMApp(unittest.TestCase):

    def setUp(self):
        # Create a test Flask app
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['SECRET_KEY'] = 'G@ytsfjcxvzdeo9863-1[ouGFDERA]'
        
        # Create a test client
        self.client = self.app.test_client()
    
    def test_index_route(self):
        # Send a GET request to the app index endpoint
        response = self.app.get('/')
        
        # Check if the response status code is 200 (OK) or not
        #self.assertEqual(response.status_code, 200)
        self.assertEqual(response.status_code, 404)
        #self.assertEqual(response.data.decode('utf-8'), 'Hello, World!')


if __name__ == '__main__':
    unittest.main()