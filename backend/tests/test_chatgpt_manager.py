from  backend.app.LLMClient import AutoGenLLMClient
from  backend.app.helpers import InMemoryResponseManager
import unittest
from typing import List, Dict
from dataclasses import dataclass
from  backend.app.configs.auto_gen import autogen_agent_config
from  backend.app import LLM_Config
from  shared.models import Enviroment
from  backend.app.helpers import templateManager
from  backend.app.templates import example_strings
# Unit Tests

# TODO: find a way to test this 
class TestAutoGenClient(unittest.TestCase):
    
    def setUp(self):
        self.response_manager = InMemoryResponseManager()
        self.client = AutoGenLLMClient(config=autogen_agent_config, response_manager=self.response_manager, LLMConfig=LLM_Config)
    def test_configure_agents_valid(self):
        #self.client = AutoGenLLMClient(config=autogen_agent_config, response_manager=None, LLMConfig=LLM_Config)
        for i in range(len(self.client.agents)):
            assert self.client.agents[i].name == autogen_agent_config["agents"][i]["name"]

    # def test_autogen_groupchat(self):
    #     json = {
    #         "robotLinks": [1,2,3],
    #         "goalPosition": [0,0,0],
    #         "NumberOfRobots": 3,
    #         "initialPositions": [0,10,1]
    #     }
    #     environment = Enviroment(**json)
    #     print(environment.model_dump())




    #     prompt = templateManager(environment=environment.model_dump() , 
    #                             tasks=["go up", "go left", "go right", "go down"],
    #                             example_one= example_strings.example1_prompt,
    #                             example_two = example_strings.example2_prompt

    #                             )
    #     self.client = AutoGenLLMClient(config=autogen_agent_config, response_manager=None, LLMConfig=LLM_Config)
    #     self.client.call(message=prompt)
    
        
    def test_autogen_memory(self):
        json = {
            "robotLinks": [1,2,3],
            "goalPosition": [0,0,0],
            "NumberOfRobots": 3,
            "initialPositions": [0,10,1]
        }
        environment = Enviroment(**json)
        #print(environment.model_dump())
        prompt = templateManager(environment=environment.model_dump() , 
                                tasks=["go up", "go left", "go right", "go down"],
                                example_one= example_strings.example1_prompt,
                                example_two = example_strings.example2_prompt

                                )
        self.client.call(message=prompt)
        
        for agent in self.client.agents:
            group_messages = self.client.manager.chat_messages_for_summary(agent=agent)
            for i in group_messages:
                self.client.add_memory(role=i["role"], content =i["content"])


        #print(self.client.getHistory())
        # for agent in self.client.agents:
        #     group_messages = self.client.manager.chat_messages_for_summary(agent=agent)
        #     for index,iter in enumerate(self.client.response_manager):
        #         for i in group_messages[index].keys:
        #             print("printing keys" , i)
        #         assert group_messages[index].keys == iter.keys
        #         # assert group_messages[index].value == iter.value