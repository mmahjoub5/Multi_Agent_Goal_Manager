from typing import Literal


from backend.app.helpers import LLMResponseManager

from dataclasses import dataclass
from typing import List, Dict, AnyStr, Union
import requests
from dotenv import load_dotenv

from enum import Enum
from abc import ABC, abstractmethod
from autogen import ConversableAgent, AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager, register_function
from shared.models import TaskResponse
from backend.app.schema import task_request_schema

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
        self.response_manager.add_response(**kwargs)

    
    def get_history(self) -> LLMResponseManager:
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
            "temperature": temparture,
            "response_format": {
                "type": "json_schema",
                "json_schema": task_request_schema
            }

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
    

# class GeminiClient(LLMClientBase):

#     def __init__(self, api, base_url):
#         super().__init__(api, None)
#         self.client = genai.Client(api_key=api)
    
#     def prepare_payload(self):
#         pass
        
#     def call(self, **kwargs):
#         required_keys = ["model", "contents"]
#         for key in required_keys:
#             if key not in kwargs:
#                 raise ValueError(f"Missing required parameter: '{key}'")
        
#         try:
#             response = self.client.models.generate_content(
#                 model=kwargs["model"], contents=kwargs["contents"]
#             )
#         except Exception as e:
#             raise ValueError(f"Error during content generation: {e}")
        
#         return response.text
    
#     def parse_response(self, **kwargs):
#         pass



    
class AutoGenAgentFactory:
    class AgentType(Enum):
        ASSISTANT = "assistant"
        USER_PROXY = "user_proxy"
        CONVERSABLE = "conversable"
    def __init__(self, llm_config: Dict):
        self.llm_config = llm_config
    def configure_agents_from_config(self, config:Dict) :
        agents = []
        for agent_config in config["agents"]:
            agent_type = self.AgentType[agent_config["type"].upper()]
            
            match agent_type:
                case self.AgentType.ASSISTANT:
                    agent = self.create_assistant_agent(**agent_config)
                case self.AgentType.USER_PROXY:
                    agent = self.create_user_proxy_agent(**agent_config)
                case self.AgentType.CONVERSABLE:
                    agent = self.create_conversable_agent(**agent_config)
                case  _:
                    raise ValueError(f"Unknown agent type: {agent_config['type']}")
            
            agents.append(agent)
        if len(agents) > 2:
            groupChat = GroupChat(agents=agents, messages=[], max_round=6, allow_repeat_speaker=True)
        else:
            groupChat = GroupChat(agents=agents, messages=[], max_round=6, allow_repeat_speaker=True, speaker_selection_method='round_robin')
        manager = GroupChatManager(groupchat=groupChat, llm_config={"config_list": self.llm_config})
        return manager, agents
    
    def create_assistant_agent(self, name:str, system_message:str, **kwargs):
        try :
            return AssistantAgent(
                name=name,
                system_message= system_message,
                llm_config={"config_list":  self.llm_config},
                code_execution_config=kwargs.get("code_execution_config", False),  # Turn off code execution, by default it is off.
                function_map= kwargs.get("function_map", None),  # No registered functions, by default it is None.
                human_input_mode=kwargs["human_input_mode"],  # Never ask for human input.
                max_consecutive_auto_reply = kwargs.get("max_consecutive_auto_reply", None),
            )
        except KeyError as e:
        # Handle missing required keys
            print(f"Required key missing from kwargs: {e}")
            raise
        except Exception as e:
            # Handle any other unexpected error
            print(f"An unexpected error occurred while creating assistant agent: {e}")
            raise
            
    def create_user_proxy_agent(self, name:str, system_message:str,  **kwargs):
        try:
            return UserProxyAgent(
                name=name,
                system_message= system_message,
                llm_config={"config_list": self.llm_config},
                code_execution_config=kwargs.get("code_execution_config", False),  # Turn off code execution, by default it is off.
                function_map= kwargs.get("function_map", None),  # No registered functions, by default it is None.
                human_input_mode=kwargs["human_input_mode"],  # Never ask for human input.
                max_consecutive_auto_reply = kwargs.get("max_consecutive_auto_reply", None),
            )
        except KeyError as e:
        # Handle missing required keys
            print(f"Required key missing from kwargs: {e}")
            raise
        except Exception as e:
            # Handle any other unexpected error
            print(f"An unexpected error occurred while creating assistant agent: {e}")
            raise
        

    def create_conversable_agent(self, name:str, system_message:str, **kwargs) -> ConversableAgent:
        try:
            return ConversableAgent(
                name=name,
                system_message= system_message,
                llm_config={"config_list": self.llm_config},
                code_execution_config=kwargs.get("code_execution_config", False),  # Turn off code execution, by default it is off.
                function_map= kwargs.get("function_map", None),  # No registered functions, by default it is None.
                human_input_mode=kwargs["human_input_mode"],  # Never ask for human input.
                max_consecutive_auto_reply = kwargs.get("max_consecutive_auto_reply", None),
            )
        except KeyError as e:
        # Handle missing required keys
            print(f"Required key missing from kwargs: {e}")
            raise
        except Exception as e:
            # Handle any other unexpected error
            print(f"An unexpected error occurred while creating assistant agent: {e}")
            raise



class AutoGenLLMClient(LLMClientBase):
    def __init__(self, LLMConfig: Dict, response_manager, config:Dict):
        super().__init__(api=None, base_url=None, response_manager=response_manager)
        self.LLMConfig = LLMConfig
        if config is not None:
            agent_factory = AutoGenAgentFactory(LLMConfig)
            self.manager, self.agents = agent_factory.configure_agents_from_config(config=config)
    
    def prepare_payload(self, **kwargs):
        pass
    
    def parse_response(self, message:str):
        pass
    def call(self, message:str, **kwargs):
        return self.agents[0].initiate_chat(self.manager, message=message)
    

    
    
    def get_agent(self, index):
        return self.agents[index]
