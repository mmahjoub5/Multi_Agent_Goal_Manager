from fastapi import FastAPI, BackgroundTasks, HTTPException
from typing import Dict
from  backend.app.configs.auto_gen import autogen_agent_config
from  backend.app.configs.config import ROBOTTABLE, logger
from  shared.models import *
from  backend.app.chains import one_llm_chain, two_llm_chain, autogen_chain, reprompt_llm_chain
from  backend.app.helpers import templateManager, reprompt_template
from  shared.rabbitmq_manager import RabbitMQConsumerManager
from datetime import datetime
import json
from pydantic import ValidationError
from  backend.app.configs.config import rabbitmq_client
from enum import Enum
from  backend.app.domain.documents import RobotDocument, TaskDocument
import time
import uuid
from bson.binary import Binary
import logging
from backend.app.db.mongo import connection 
from pymongo.errors import *
from backend.app.domain.base.nosql import NoSQLBaseDocument

# initialize app
app = FastAPI()


# Configure database 
NoSQLBaseDocument.configure_database_connection("robotarm_db")

class TASK_CONTROLLER_TYPE(Enum):
    ONE_LLM = "one_llm"
    TWO_LLM = "two_llm"
    AUTOGEN = "autogen"

def validate_and_process_tasks(tasks_json,robot_id):
    """Validate and process the task JSON."""
    for i, val in enumerate(tasks_json["TASK"]):
        val["tasks"] = ROBOTTABLE[robot_id]["Task_List"]
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
       
    
    
    robotDoc:RobotDocument = ROBOTTABLE[packet.robot_id]["Doc"]
    if robotDoc is None:
        raise KeyError("robot id not in robot table, so end point /setGoal was never called")
    
    prompt = templateManager(environment=packet.environment, 
                            tasks=robotDoc.robot.possible_tasks,
                            robot_capabilities=robotDoc.robot.robot_capabilities[0],
                            robot_type=robotDoc.robot.robot_type,
                            goal=robotDoc.robot.goal_specifications)
    
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


consumer_manager = RabbitMQConsumerManager(rabbitmq_client)
consumer_manager.start_consumer("task_request", callback=on_task_request_callback)


'''

    ROBOTS

'''
@app.get("/robots")
def get_all_robot(response_model=GetAllRobotsResponse):
    """
    Retrieves a list of all robots from the database and returns their metadata.

    Response:
    - Returns a `GetAllRobotsResponse` containing a list of robots.

    Raises:
    - RuntimeError: If any exception occurs during the data fetching or serialization process.
    """
    robots  = []
    try :
        robots = RobotDocument.find_all()
        robots =[i.robot for i in robots]
    except Exception as e:
        logger.error(f"Serialization error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error: Serialization Failed")
    return GetAllRobotsResponse(robots=robots)
    

@app.get("/robots/{robot_id}")
def get_robot_by_id(robot_id:str, response_model=GetRobotByIDResponse):
    """
    Retrieves metadata for a specific robot identified by its ID.

    Parameters:
    - robot_id (str): The unique identifier of the robot to retrieve.

    Response:
    - Returns a `GetRobotByIDResponse` containing the metadata of the specified robot.

    Raises:
    - RuntimeError: If any exception occurs during the database query or serialization process.
    """
    try :
        robot_doc:RobotDocument = RobotDocument.find(_id=robot_id)
        
    
    except Exception as e:
        logger.error(f"Serialization error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error: Serialization Failed")
    return GetRobotByIDResponse(robot=robot_doc.robot)




@app.post("/robots/register", response_model=RegisterRobotResponse)
def register_robot(packet:RegisterRobotRequest):
    """
    Registers a new robot and updates the global ROBOTTABLE with its details.

    Parameters:
    - packet (RegisterRobotRequest): The request payload containing robot information.

    Response:
    - Returns a `RegisterRobotResponse` with the registration timestamp and the robot ID.

    Raises:
    - RuntimeError: If robot creation/retrieval fails.
    - KeyError: If the robot ID already exists in the ROBOTTABLE.
    - ValueError: If the `RobotDocument` does not contain a valid `possible_tasks` list.
    """
    try: 
        robot_doc = RobotDocument(robot=packet.robot,
                              task_ids=[])
    except Exception as e:
        logger.error(f"Serialization error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error: Serialization Failed")

    try :
        robot_doc:RobotDocument = RobotDocument.create(filter_doc=robot_doc)
    except Exception as e:
        logger.error(f"Failed to create or retrieve RobotDocument: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error: Failed to create or retrieve RobotDocument")

    
    robot_id = robot_doc.id

    if robot_id in ROBOTTABLE:
        logger.error(f"Robot ID {robot_id} already exists in ROBOTTABLE")
        raise HTTPException(status_code=400, detail=f"Robot ID {robot_id} already exists in ROBOTTABLE")
   
    
    # Validate robot_doc and extract possible tasks
    if not hasattr(robot_doc.robot, "possible_tasks") or not isinstance(robot_doc.robot.possible_tasks, list):
        logger.error("RobotDocument does not contain a valid 'possible_tasks' list")
        raise HTTPException(status_code=400,detail="RobotDocument does not contain a valid 'possible_tasks' list")


    task_list = [task["task_name"] for task in robot_doc.robot.possible_tasks]


    # UPDATE CACHE 
    ROBOTTABLE[robot_id] = {
        "Doc": robot_doc,
        "Task_List": task_list,
    }   
    

    response = RegisterRobotResponse(
                            robot_id = str(robot_id)
                            )
    return response


# remove robot 
@app.delete("/robots/{robot_id}")
def delete_robot_by_id(robot_id:str, response_model = DeleteRobotResponse):
    """
    Deletes a robot from the system by its ID.

    Parameters:
    - robot_id (str): The unique identifier of the robot to delete.
    - response_model (DeleteRobotResponse): The response model indicating the success of the deletion.

    Raises:
    - HTTPException: If the robot is not found in `ROBOTTABLE` or in the database.
    - RuntimeError: If an unexpected error occurs during the deletion process.

    Response:
    - Returns a `DeleteRobotResponse` with:
        - `status`: Boolean indicating success (`True`).
        - `time`: The UTC timestamp of the deletion.
    """
    # Logic to remove the robot from the system
    if robot_id not in ROBOTTABLE:
        logger.error("Robot not found")
        raise HTTPException(status_code=404, detail="Robot not found")
    try :
        number_removed = RobotDocument.remove_document(_id=robot_id)
        logger.error("Document Not found")
        if number_removed == 0:
            raise HTTPException(status_code=404, detail="Document Not found")
    except Exception as e:
        logger.error(f"Failed to retrieve RobotDocument: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: Failed to recieve document {e}")
        
    return DeleteRobotResponse(status=True)
    



'''
    TASKS

'''
#TODO:  Get tasks in the system
@app.get("/task/")
def get_all_task():
    pass

#TODO: Get task in system by task id
@app.get("/task/{task_id}")
def get_task_by_id():
    pass

@app.post("/task/register", response_model=RegisterTaskResponse)
def registerTask(packet:RegisterTaskRequest):
    """
    Registers a new task and associates it with a specific robot.

    Args:
        packet (RegisterTaskRequest): Incoming request with task details.

    Returns:
        RegisterTaskResponse: Response indicating the task registration status.
    """
     # Step 1: Extract task data and create TaskDocument
    task = packet.task
    try:
        task_doc = TaskDocument(task=task, 
                                status=STATUS.IN_PROGRESS.value, # TODO: Neeed to make this pending but dont have logic for it yet
                                response_ids=[])
    except Exception as e:
        logger.error(f"failed to serialize Task Document {e}")
        raise HTTPException(status_code=500, detail="Internal Error: Failed to Serialize request")
    
    # Step 2: create task document, update robot documents with new task IDs
    # TODO: make capability to update more than one document 

    try:
        task_doc:TaskDocument = TaskDocument.create(filter_doc=task_doc.id)
        task_id = task_doc.id
        robot_id = task_doc.task.robot_id
        updated_count = RobotDocument.update_document(
            filter={"_id": robot_id},
            update={"$addToSet": {"task_ids": str(task_id)}}
        )
        if updated_count == 0:
            logger.error(f"Failed to update robot with ID {task_doc.task.robot_id}. Robot not found or no changes made.")
            task_id = uuid.uuid4()
            bson_uuid = Binary.from_uuid(task_id)

            number_removed = TaskDocument.remove_document(_id=str(task_id))
            raise HTTPException(status_code=400, detail=f"Internal Server Error:  ROBOT ID NOT FOUND")
    except (ConnectionFailure, OperationFailure, WriteError, WriteConcernError) as e:
        logger.error(f"MongoDB error occurred: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error:")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        
        raise HTTPException(status_code=500, detail=f"Internal Server Error:")



    
    
    # step 4 update cache 
    # TODO: 
    # if robot_id not in ROBOTTABLE:
    #     raise KeyError(f"{robot_id} has not been registered")
    #ROBOTTABLE[robot_id][task_id] = task_doc

    return RegisterTaskResponse(task_id=str(task_id),
                                status=STATUS.PENDING)



@app.post("/goalReached", response_model=GoalReachedResponse)
def goal_reached(packet:GoalReachedRequest):
    robot_id = packet.robot_id
    task_id = packet.task_id
    if robot_id in ROBOTTABLE:
        if task_id in ROBOTTABLE[robot_id]:
            task_doc:TaskDocument = ROBOTTABLE[robot_id][task_id]
            try:
                TaskDocument.update_document(filter={"_id": task_doc.id},
                                         update={"$set": {"status": str(STATUS.COMPLETE)}})
            except Exception as e:
                raise RuntimeError(f"{e}")
        else: 
            raise HTTPException(status_code=404, detail="Task not found")
        del ROBOTTABLE[robot_id][task_id]
    else:
        try:
            update_count = TaskDocument.update_document(filter={"_id": uuid.UUID(task_id)},
                                        update={"$set": {"status": str(STATUS.COMPLETE)}})  
        except Exception as e:
            logger.error(f"error when updating database{e}")
            raise HTTPException(status_code=500, detail="Internal Server Error: Unable to update Database")
        if update_count == 0:
            logger.error("no documents were updated")
            raise HTTPException(status_code=400, detail="TASK NOT FOUND")
    
            

    return GoalReachedResponse(
        status=STATUS.COMPLETE,
        message="Task status updated successfully and removed from cache."
    )
   
   



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


    



