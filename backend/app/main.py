from fastapi import FastAPI, BackgroundTasks
from typing import Dict
from  backend.app.configs.auto_gen import autogen_agent_config
from  backend.app.configs.config import ROBOTTABLE, TASKLIST
import pdb
from  shared.models import TaskRequest, TaskResponse, SetGoalRequest, SetGoalResponse, TaskFeedback
from  backend.app.chains import one_llm_chain, two_llm_chain, autogen_chain, reprompt_llm_chain
from  backend.app.helpers import templateManager, reprompt_template
from  shared.rabbitmq_manager import RabbitMQConsumerManager
from datetime import datetime
import json
from pydantic import ValidationError
from  backend.app.configs.config import rabbitmq_client
from enum import Enum
import threading
from  backend.app.domain.documents import RobotDocument
import re
import time
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

def validate_and_process_tasks(tasks_json,robot_id):
    """Validate and process the task JSON."""
    for i, val in enumerate(tasks_json["TASK"]):
        val["tasks"] = TASKLIST[robot_id]
    return TaskFeedback(**tasks_json)

def on_task_request_callback(ch, method, properties, body):
    ch.basic_ack(delivery_tag=method.delivery_tag)
    try:
        decoded_message = body.decode()
        message_data:dict = json.loads(decoded_message)
        packet = TaskRequest(**message_data)
    except json.JSONDecodeError:
        raise SystemError("Error: Invalid JSON format")
        
    except ValidationError as e:
        raise ValidationError(f"Error deserializing message: {e}")
        
    except Exception as e:
        raise RuntimeError(f"Unexpected error during deserialization: {e}")
       
    
    
    robotDoc:RobotDocument = ROBOTTABLE[packet.robot_id]
    if robotDoc is None:
        raise KeyError("robot id not in robot table, so end point /setGoal was never called")
    
    prompt = templateManager(environment=packet.environment, 
                            tasks=robotDoc.possible_tasks,
                            robot_capabilities=robotDoc.robot_capabilities[0],
                            robot_type=robotDoc.robot_type,
                            goal=robotDoc.goal_specifications)
    
    task_controller_type = TASK_CONTROLLER_TYPE[packet.task_controller_type.upper()]
    match task_controller_type:
        case TASK_CONTROLLER_TYPE.ONE_LLM:
            response:TaskResponse = one_llm_chain(prompt, packet.task_controller_model)
        case TASK_CONTROLLER_TYPE.TWO_LLM:
            response:TaskResponse = two_llm_chain(prompt, packet.task_controller_model)
        case TASK_CONTROLLER_TYPE.AUTOGEN:
            response:TaskResponse = autogen_chain(prompt, packet.task_controller_model)
        case _:
            raise ValueError(f"Unknown TASK_CONTROLLER_TYPE type: {packet.task_controller_type}")
    
    if response is not None:
        tasks_for_client = response.message[-1]["content"]   
        task_json = json.loads(tasks_for_client)
        try:
            feedback = validate_and_process_tasks(tasks_json=task_json, robot_id=packet.robot_id)
        except ValidationError as e:
            prompt = reprompt_template(str(e))
            time.sleep(2)
            response:TaskResponse = reprompt_llm_chain(prompt, response, packet.task_controller_model)
            if response is not None:
                tasks_for_client = response.message[-1]["content"]   
                task_json = json.loads(tasks_for_client)    
                try :
                    feedback = validate_and_process_tasks(tasks_json=task_json, robot_id=packet.robot_id)
                except ValidationError as secondErrror:
                    # TODO: should we we prompt again? 
                    raise ValidationError("Validation Error:", secondErrror)


        rabbitmq_client.send_message("task_feedback", message={"response":feedback.model_dump()})
    else:
        raise SystemError("GPT CONTROLLER RESPONSE IS NONE")


    
@app.post("/setGoal", response_model=SetGoalResponse)
def setGoal_and_startQs(packet:SetGoalRequest):
    # get robot meta data 

    robot_doc = RobotDocument.get_or_create_from_request(request=packet)

    robot_id = packet.robot_locations[0].robot_id 
    # Combine robot_controls and robot_computations into one list
    
    ROBOTTABLE[robot_id] = robot_doc
    TASKLIST[robot_id] = [task["task_name"] for task in robot_doc.possible_tasks]
    
    

    # TODO: update robot meta data and id to DB
    consumer_manager.start_consumer("task_request", callback=on_task_request_callback)

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





# @app.post("/taskPlaningTwoGPT", response_model=TaskResponse)
# def get_task_one_gpt(packet:TaskRequest):
    
#     # TODO: do one chat gpt call to create a prompt based on pose and enviroment and maybe history of certain examples 
#     prompt = templateManager(enviroment=packet.environment, tasks=packet.tasks) 
#     response = two_llm_chain(prompt)

#     return response.model_dump()


# @app.post("/taskPlaningOneGPT4", response_model=TaskResponse)
# def get_task_two_gpt(packet:TaskRequest):
#     prompt = templateManager(environment=packet.environment, tasks=packet.tasks)
#     response = one_llm_chain(prompt)
#     return response.model_dump()
   
    
# @app.post("/autogen", response_model=TaskResponse)
# def get_task(packet:TaskRequest):
#     prompt = templateManager(newInput=packet)
    
#     return response.model_dump()


    



