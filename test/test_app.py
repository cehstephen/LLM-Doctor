import unittest
import unittest
import sys
import os
import requests
import openai
from decouple import config

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

    def test_post_with_proper_payload(self):
        openai.api_key = config('MY_OPEN_AI_SECRET_KEY')
        URL = "https://api.openai.com/v1/chat/completions"
        ai_model_name = 'gpt-3.5-turbo'
        healthInputCase = "what is fever, in summary?"
        payload = {
                "model": ai_model_name,
                "temperature" : 1.0,
                "messages" : [
                     {"role": "user", "content": f"{healthInputCase} "},
                    ]
                }        
        headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {openai.api_key}"
                }
        ai_response = requests.post(URL, headers=headers, json=payload)
        assert ai_response.status_code, 200


if __name__ == '__main__':
    unittest.main()