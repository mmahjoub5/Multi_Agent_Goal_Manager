from typing import Literal

from pydantic import BaseModel, Field
from app.helpers import LLMResponseManager
from typing_extensions import Annotated
from dataclasses import dataclass
from typing import List, Dict, AnyStr
import autogen
import requests
from dotenv import load_dotenv
import os
import pdb

from abc import ABC, abstractmethod
from google import genai
from google.genai import types
import pdb

class LLMClientBase(ABC):
    def __init__(self, api:str, base_url:str, response_manager:LLMResponseManager):
        self.api = api 
        self.base_url = base_url
        self.response_manager = response_manager


    @abstractmethod
    def prepare_payload(self, **kwargs):
        pass

    @abstractmethod
    def call(self, **kwargs):
        pass

    @abstractmethod
    def parse_response(self, **kwargs) ->List:
        pass

    def add_memory(self, **kwargs ) -> None:
        self.response_manager.add_response(kwargs["role"], kwargs["content"])

    
    def getHistory(self) -> LLMResponseManager:
        return self.response_manager.messages


class AzureAIClient(LLMClientBase):
    def __init__(self, api:str, base_url:str, deployment_name:str, api_version:str, response_manager):
        super().__init__(api, base_url, response_manager=response_manager)
        self.api_version = api_version
        self.deployment_name = deployment_name
        

        # Headers
        self.headers = {
            "Content-Type": "application/json",
            "api-key": self.api
        }

    def api_call(self, **kwargs) -> Dict:
        response = requests.post(self.uri, headers=self.headers, json=kwargs["payload"])
        
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise ValueError(f"Request failed: {response.status_code} - {response.text}") from e
        
        return response.json()

    
    
    

class GPTCompletionClient(AzureAIClient):
    def __init__(self, api, base_url, api_version, deployment_name, response_manager):
        super().__init__(api, base_url, api_version, deployment_name, response_manager)
        self.uri = f"{base_url}/openai/deployments/{deployment_name}/completions?api-version={api_version}"

    def prepare_payload(self, prompt:str, max_tokens:int = 300, choices:int = 1, temparture:float = 0.7):
         # Payload for chat/completions
        return {
            "prompt": prompt,
            "max_tokens": max_tokens,
            "n": choices,
            "temperature": temparture
        }
        
    def call(self, **kwargs):
        if "prompt" not in kwargs:
            raise ValueError("Missing required parameter: 'prompt'")
        
        payload = self.prepare_payload(**kwargs)
        return self.api_call(payload=payload)

        
    def parse_response(self, response:Dict) -> List:
        msgs = []
        for choice in response["choices"]:
            msgs.append(choice["text"])
        return msgs

class GPTChatCompletionClient(AzureAIClient):
    def __init__(self, api, base_url, api_version, deployment_name, response_manager):
        super().__init__(api, base_url, api_version=api_version, deployment_name=deployment_name, response_manager=response_manager)
        self.uri = f"{self.base_url}/openai/deployments/{self.deployment_name}/chat/completions?api-version={self.api_version}"
       
        
    def prepare_payload(self, messages:List[Dict[str,str]], max_tokens:int = 300, choices:int = 1, temparture:float = 0.7):
        return {
            "messages": messages,
            "max_tokens": max_tokens,
            "n": choices,
            "temperature": temparture
        }

    def call(self,**kwargs) -> Dict:
        if "messages" not in kwargs:
            raise ValueError("Missing required parameter: 'messages'")
        payload = self.prepare_payload(**kwargs)
        return self.api_call(payload=payload)
        
    
    def parse_response(self, response:Dict) -> List:
        msgs = []
        for choice in response["choices"]:
            msgs.append(choice["message"]["content"])
        return msgs
    

class GeminiClient(LLMClientBase):
    def __init__(self, api, base_url):
        super().__init__(api, None)
        self.client = genai.Client(api_key=api)
    
    def prepare_payload(self):
        pass
        
        
    def call(self, **kwargs):
        required_keys = ["model", "contents"]
        for key in required_keys:
            if key not in kwargs:
                raise ValueError(f"Missing required parameter: '{key}'")
        
        try:
            response = self.client.models.generate_content(
                model=kwargs["model"], contents=kwargs["contents"]
            )
        except Exception as e:
            raise ValueError(f"Error during content generation: {e}")
        
        return response.text
    
    def parse_response(self, **kwargs):
        pass






