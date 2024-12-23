from fastapi import FastAPI, BackgroundTasks
from typing import Dict
from ipr_worlds.backend.app.configs.auto_gen import autogen_agent_config
import pdb
from ipr_worlds.shared.models import TaskRequest, TaskResponse, SetGoalRequest, SetGoalResponse, Enviroment
from ipr_worlds.backend.app.chains import one_llm_chain, two_llm_chain, autogen_chain
from ipr_worlds.backend.app.helpers import templateManager
from ipr_worlds.shared.rabbitmq_manager import RabbitMQConsumerManager
from datetime import datetime
import json
from pydantic import ValidationError
from ipr_worlds.backend.app.configs.config import rabbitmq_client
from enum import Enum
import threading

# initialize app
app = FastAPI()
consumer_manager = RabbitMQConsumerManager(rabbitmq_client)

'''
    EndPoint set by request to start set goal and connection to the high level controller
    1. Client will provide meta data message about enviroment(hard coded for now):
        - robot type(s)
        - Number of Robots
        - Robot Capabilities
    2. Robot Locations
    3. Goal Specifications
    4. Task Description
        - what the task the client is asking 
    5. Environment Constraints
    6. Goal Specifications:
    7. Communication Protocol (dont need for now)
    8. Performance Metrics (dont need for now)
    9.sets up RabitMQ client
    10. sets up Autogen/LLMClient objects
    11. sets up call backs for all the message queue topics 

'''

class TASK_CONTROLLER_TYPE(Enum):
    ONE_LLM = "one_llm"
    TWO_LLM = "two_llm"
    AUTOGEN = "autogen"

def on_task_request_callback(ch, method, properties, body):
    try:
        packet = TaskRequest.model_validate_json(body.decode())
    except ValidationError as e:
        print(f"Error deserializing message: {e}")
    except Exception as e:
        print(f"Unexpected error during deserialization: {e}")
    ch.basic_ack(delivery_tag=method.delivery_tag)
    prompt = templateManager(environment=packet.environment, tasks=packet.tasks)
    task_controller_type = TASK_CONTROLLER_TYPE[packet.task_controller_type.upper()]
    
    if task_controller_type == TASK_CONTROLLER_TYPE.ONE_LLM:
        response:TaskResponse = one_llm_chain(prompt)
    elif task_controller_type == TASK_CONTROLLER_TYPE.TWO_LLM:
        response:TaskResponse = two_llm_chain(prompt)
    elif task_controller_type == TASK_CONTROLLER_TYPE.AUTOGEN:
        response:TaskResponse = autogen_chain(prompt)
    else:
        raise ValueError(f"Unknown TASK_CONTROLLER_TYPE type: {packet.task_controller_type}")
    
    if response is not None:
        rabbitmq_client.send_message("task_feedback", message={"response":response.model_dump_json()})



    
@app.post("/setGoal", response_model=SetGoalResponse)
def setGoal_and_startQs(packet:SetGoalRequest):

    # TODO: update robot meta data and id to DB
    consumer_manager.start_consumer("task_request", callback=on_task_request_callback)
    #consumer_manager.start_consumer("task_feedback", callback=on_task_feedback_callback)


    print("Consumer thread started, processing RabbitMQ messages in the background.")
    response = SetGoalResponse(
                            topicNames=[f"task_request", f"task_feedback"], 
                            time = datetime.utcnow().isoformat())
    return response
    


@app.post("/goalReached")
def close_connection(packet:SetGoalRequest):
   pass
@app.get("/async")
async def getAsync():
    return {"value":"you are async gay"}

# end point 
@app.post("/task")
def submit_task(task: Dict, background_task: BackgroundTasks):
    pass





@app.post("/taskPlaningTwoGPT", response_model=TaskResponse)
def get_task_one_gpt(packet:TaskRequest):
    
    # TODO: do one chat gpt call to create a prompt based on pose and enviroment and maybe history of certain examples 
    prompt = templateManager(enviroment=packet.environment, tasks=packet.tasks) 
    response = two_llm_chain(prompt)

    return response.model_dump()


@app.post("/taskPlaningOneGPT4", response_model=TaskResponse)
def get_task_two_gpt(packet:TaskRequest):
    prompt = templateManager(environment=packet.environment, tasks=packet.tasks)
    response = one_llm_chain(prompt)
    return response.model_dump()
   
    
# @app.post("/autogen", response_model=TaskResponse)
# def get_task(packet:TaskRequest):
#     prompt = templateManager(newInput=packet)
    
#     return response.model_dump()


    



