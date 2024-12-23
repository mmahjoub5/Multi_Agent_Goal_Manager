from ipr_worlds.backend.app.LLMClient import GPTChatCompletionClient, GPTCompletionClient, GeminiClient, AutoGenLLMClient
from ipr_worlds.backend.app.helpers import InMemoryResponseManager
import opik
from ipr_worlds.backend.app.helpers import InMemoryResponseManager
from ipr_worlds.shared.models import TaskRequest, TaskResponse
from ipr_worlds.backend.app.configs.config import *
from ipr_worlds.backend.app.configs.auto_gen import autogen_agent_config
from ipr_worlds.backend.app import LLM_Config
from ipr_worlds.backend.app.templates import example_strings
''''
    Function taks in the enviroment from client and a end goal from client robot
    CHAIN is posted to OPIK to log the input and the output
    Returns a list of concise task the robot needs to follow


'''
@opik.track
def two_llm_chain(prompt:str) -> TaskResponse:
    response_manager = InMemoryResponseManager()
    

    completion_client = GPTCompletionClient(OPENAI_KEY_COMPLETION, 
                                        ENDPOINT_COMPLETION, 
                                        api_version=COMPLETION_VERSION, 
                                        deployment_name=COMPLETION_DEPLOYMENT_NAME,
                                        response_manager=response_manager)
    
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
    

    chat_client = GPTChatCompletionClient(api=OPENAI_KEY_CHAT,
                                         base_url=ENDPOINT_CHAT,
                                         api_version=CHAT_VERSION,
                                         deployment_name=CHAT_DEPLOYMENT_NAME,
                                         response_manager=response_manager)

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
def one_llm_chain(prompt:str) -> TaskResponse:
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
    chat_client = GPTChatCompletionClient(api=OPENAI_KEY_CHAT,
                                         base_url=ENDPOINT_CHAT,
                                         api_version=CHAT_VERSION,
                                         deployment_name=CHAT_DEPLOYMENT_NAME,
                                         response_manager=response_manager)
    chat_response = chat_client.call(messages=messages)
    msgs = chat_client.parse_response(chat_response)
    
    for i in msgs:
        chat_client.add_memory(role = "assistant", content = i)

    # update database with previous chats and movements 
    response = TaskResponse(message=chat_client.get_history())
    return response

@opik.track
def autogen_chain(prompt:str) -> TaskResponse:
    response_manager = InMemoryResponseManager()
    autogen_client:AutoGenLLMClient = AutoGenLLMClient(config=autogen_agent_config, response_manager=response_manager, LLMConfig=LLM_Config)
    autogen_client.call(message=prompt)
    
    for agent in autogen_client.agents:
        group_messages = autogen_client.manager.chat_messages_for_summary(agent=agent)
        for i in group_messages:
            autogen_client.add_memory(role=i["role"], content =i["content"])
    
    reponse = TaskResponse(message=autogen_client.get_history())
    return reponse