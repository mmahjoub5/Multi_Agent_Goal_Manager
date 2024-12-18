from fastapi import FastAPI, BackgroundTasks
from typing import Dict
from pydantic import BaseModel
from typing import List, Dict
from jinja2 import Environment, FileSystemLoader
from app.gpt import GPTChatCompletionClient, GPTCompletionClient, GeminiClient
from app.helpers import InMemoryResponseManager
import pdb
from dotenv import load_dotenv
import os 

class Enviroment(BaseModel):
    robotLinks:List
    goalPosition: List
    NumberOfRobots:int
    initialPositions:List

import opik



# Define input structure
class TaskRequest(BaseModel):
    environment:Enviroment  # Details of the environment (e.g., objects, obstacles)



# Define output structure
class TaskResponse(BaseModel):
    message: List[Dict[str,str]]
   
# Load environment variables at the start of your application
load_dotenv()
OPENAI_KEY_CHAT = os.getenv("AZURE_OPENAI_KEY")
ENDPOINT_CHAT = os.getenv("AZURE_OPENAI_ENDPOINT")

OPENAI_KEY_COMPLETION = os.getenv("AZURE_OPENAI_KEY_2")
ENDPOINT_COMPLETION = os.getenv("AZURE_OPENAI_ENDPOINT_2")

COMPLETION_VERSION = "2024-08-01-preview"  # Update if needed
 # Endpoint URL for the deployment
COMPLETION_DEPLOYMENT_NAME = "davinci-002"   # Replace with your deployed model name

# OPIK KEY 
OPIK_KEY = os.getenv('OPIK_KEY')
opik.configure(api_key=OPIK_KEY)
 # API version
CHAT_VERSION = "2024-08-01-preview"  # Update if needed
    # Endpoint URL for the deployment
CHAT_DEPLOYMENT_NAME = "gpt-35-turbo-16k"  # Replace with your deployed model name








if not OPENAI_KEY_CHAT or not ENDPOINT_CHAT:
    raise ValueError("Please set the AZURE_OPENAI_KEY and AZURE_OPENAI_ENDPOINT environment variables.")

if not OPENAI_KEY_COMPLETION or not ENDPOINT_COMPLETION:
        raise ValueError("Please set the AZURE_OPENAI_KEY and AZURE_OPENAI_ENDPOINT environment variables.")

# archive for now
def templateManager(newInput:str):
    # load template 
    # Define the directory containing your templates
    template_dir = "app/templates"  # Adjust this to your directory structure
    env = Environment(loader=FileSystemLoader(template_dir))

    # Load the ChatGPT prompt template
    template = env.get_template("summarizeEnviroment.jinja2")
    # Define data for rendering
    data = {
        "new_input": newInput
    }

    prompt = template.render(data)
    return prompt



# initialize app
app = FastAPI()


@opik.track
# def my_llm_chain(input_text):
#     # Call the different parts of my chain
#     return input_text



@app.get("/")
def defualt():
    return {"value":"you are gay"}

@app.get("/async")
async def getAsync():
    return {"value":"you are async gay"}

# end point 
@app.post("/task")
def submit_task(task: Dict, background_task: BackgroundTasks):
    pass


@app.get("/id")
def get_id():
    return {"id":1234}

''''
    Function taks in the enviroment from client and a end goal from client robot

    Returns a list of concise task the robot needs to follow


'''
@opik.track
def chain(prompt:str) -> TaskResponse:
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
    response = TaskResponse(message=chat_client.getHistory())
    return response

@app.post("/taskPlaningTwoGPT", response_model=TaskResponse)
def get_task(packet:TaskRequest):
    
    # TODO: do one chat gpt call to create a prompt based on pose and enviroment and maybe history of certain examples 
    prompt = templateManager(newInput=packet)  
    response = chain(prompt)

    return response.model_dump()

    



