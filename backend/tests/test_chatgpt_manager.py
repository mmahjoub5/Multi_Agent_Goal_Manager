from app.gpt import ChatGPTResponseManager, chatGPTCall
import unittest
from typing import List, Dict
from dataclasses import dataclass



# Unit Tests
class TestChatGPTResponseManager(unittest.TestCase):
    def setUp(self):
        """
        Set up a fresh instance of ChatGPTResponseManager and sample data for each test.
        """
        self.manager = ChatGPTResponseManager()
        self.response_example = {
            "choices": [
                {"message": {"content": "Why don't scientists trust atoms? Because they make up everything!"}},
                {"message": {"content": "Why did the chicken join a band? Because it had the drumsticks!"}}
            ]
        }
        return super().setUp()


    def testGPTCall(self):
        messages = [
            {
                "role": "system", 
                "content": "You are an assistant. trying to solve a robotics problem", 
            },
            {
                "role": "user", 
                "content": "tell me how to pick this up based on my enviroment:"
            }
        ]


        response:ChatGPTResponseManager = chatGPTCall(messages=messages)
        for i in range(len(messages)):
            self.assertDictEqual(messages[i], response.messages[i])

        
        