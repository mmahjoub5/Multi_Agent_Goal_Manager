from  backend.app.LLMClient import GPTChatCompletionClient, GPTCompletionClient, AutoGenLLMClient
from  backend.app.helpers import InMemoryResponseManager
import opik
from  backend.app.helpers import InMemoryResponseManager, Autogen_InMemoryResponseManager
from  shared.models import TaskRequest, TaskResponse
from  backend.app.configs.config import *
from  backend.app.configs.auto_gen import autogen_agent_config
from  backend.app.templates import example_strings
from typing import Dict
from  backend.app.configs.config import rabbitmq_client

def send_task_to_low_level_controller(task:Dict):
    
    rabbitmq_client.send_message("task_feedback", message={"response":task})
    


''''
    Function taks in the enviroment from client and a end goal from client robot
    CHAIN is posted to OPIK to log the input and the output
    Returns a list of concise task the robot needs to follow


'''
@opik.track
def two_llm_chain(prompt:str, deployment_name:str) -> TaskResponse:
    response_manager = InMemoryResponseManager()
    
    if deployment_name not in API_TABLE:
        raise ValueError(f"Deployment name {deployment_name} not found in API_TABLE.")
    api_config:API_CONFIG = API_TABLE[deployment_name]

    completion_client = GPTCompletionClient(**api_config, response_manager=response_manager)
    
    updated_prompt = completion_client.call(prompt=prompt)
    updated_prompt = completion_client.parse_response(updated_prompt)
    

    # TODO: pass the prompt to another gpt call to create the tasks based on the list of possible tasks 
    messages = [
            {
                "role": "system", 
                "content": "You are an assistant. trying to solve a robotics problem", 
            },
            {
                "role": "user", 
                "content": updated_prompt[0]
            }
        ]
    
    

    chat_client = GPTChatCompletionClient(response_manager=response_manager,**api_config )

    for i in messages:
        chat_client.add_memory(role=i["role"], content = i["content"])
    
    chat_response = chat_client.call(messages=messages)
    msgs = chat_client.parse_response(chat_response)
    
    for i in msgs:
        chat_client.add_memory(role = "assistant", content = i)

    # update database with previous chats and movements 
    response = TaskResponse(message=chat_client.get_history())
    return response


@opik.track
def one_llm_chain(prompt:str, deployment_name:str) -> TaskResponse:
   # TODO: pass the prompt to another gpt call to create the tasks based on the list of possible tasks 
    messages = [
            {
                "role": "system", 
                "content": "You are an assistant. trying to solve a robotics problem", 
            },
            {
                "role": "user", 
                "content": prompt
            }
        ]
    response_manager = InMemoryResponseManager()
    for i in messages:
        response_manager.add_response(role=i["role"], content = i["content"])
    if deployment_name not in API_TABLE:
        raise ValueError(f"Deployment name {deployment_name} not found in API_TABLE.")
    api_config = API_TABLE[deployment_name]

    chat_client = GPTChatCompletionClient(response_manager=response_manager, **api_config.model_dump())
    chat_response = chat_client.call(messages=messages)
    msgs = chat_client.parse_response(chat_response)
    
    for i in msgs:
        chat_client.add_memory(role = "assistant", content = i)

    # update database with previous chats and movements 
    response = TaskResponse(message=chat_client.get_history())
    return response

@opik.track
def autogen_chain(prompt:str, deployment_name:str) -> TaskResponse:
    response_manager = Autogen_InMemoryResponseManager()
    if deployment_name not in API_TABLE:
        raise ValueError(f"Deployment name {deployment_name} not found in API_TABLE.")
    api_config:API_CONFIG = API_TABLE[deployment_name]
    LLM_Config = [
        {
            "model": api_config.deployment_name,
            "api_type": "azure",
            "api_key": api_config.api,
            "base_url": api_config.base_url,
            "api_version": api_config.api_version,
        }
    ]
    autogen_client:AutoGenLLMClient = AutoGenLLMClient(config=autogen_agent_config, response_manager=response_manager, LLMConfig=LLM_Config)
    chat_result = autogen_client.call(message=prompt)
    
    for i in chat_result.chat_history:
        autogen_client.add_memory(name = i['name'], content=i['content'])
   
    reponse = TaskResponse(message=autogen_client.get_history())
    return reponse

@opik.track
def reprompt_llm_chain(prompt:str, response:TaskResponse, deployment_name:str):
    response.message.append(
        
            {
                "role": "user", 
                "content": prompt
            }
        
    )
    response_manager = InMemoryResponseManager()
    if deployment_name not in API_TABLE:
        raise ValueError(f"Deployment name {deployment_name} not found in API_TABLE.")
    api_config = API_TABLE[deployment_name]

    chat_client = GPTChatCompletionClient(response_manager=response_manager, **api_config.model_dump())
    chat_response = chat_client.call(messages=response.message)
    msgs = chat_client.parse_response(chat_response)
    
    for i in msgs:
        chat_client.add_memory(role = "assistant", content = i)

    response = TaskResponse(message=chat_client.get_history())