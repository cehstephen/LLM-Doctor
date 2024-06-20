import unittest
import unittest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app

class TestLLMApp(unittest.TestCase):

    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['SECRET_KEY'] = 'G@ytsfjcxvzdeo9863-1[ouGFDERA]'
        self.client = self.app.test_client()
    
    def test_index_route_via_get_request(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
    
    def test_index_route_via_post_request(self):
        response = self.client.post('/')
        self.assertEqual(response.status_code, 400)


if __name__ == '__main__':
    unittest.main()