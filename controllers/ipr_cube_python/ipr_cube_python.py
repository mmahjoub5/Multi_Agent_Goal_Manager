
import os
import sys
print("Current working directory:", os.getcwd())
from libraries.ipr import IPR
from libraries.helpers import rotation_matrix_to_euler_angles
import ikpy.chain
import numpy as np
import ikpy.utils.plot as plot_utils
import re
import matplotlib.pyplot
from mpl_toolkits.mplot3d import Axes3D
# Add the path to the 'ipr_worlds' directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from  controllers.ipr_cube_python.libraries.ikpy_wrapper import IKPY_WRAPPER
from  controllers.ipr_cube_python.libraries.api_client import SYNC_APIClient, ASYNC_APIClient
from  shared.models import *
from  controllers.ipr_cube_python.libraries.api_client import SYNC_APIClient, ASYNC_APIClient
from  controllers.ipr_cube_python.json.robot_capability import robot_capability_json, task_register_json
from  shared.models import *
from  shared.rabbitmq_manager import RabbitMQ_Client, RabbitMQConsumerManager
from  controllers.ipr_cube_python.libraries.robot_controller_manager import Robot_Control_Manager
from time import sleep
import ast
import threading
import json
import pdb
import copy
import os 



script_dir = os.path.dirname(os.path.abspath(__file__))
urdf = os.path.join(script_dir, "IprHd6m180.urdf")

# Add the parent directory to sys.path
my_chain = IKPY_WRAPPER(urdf=urdf)
my_chain.active_links_mask = [False, True, True, True, True, True, True, False ]  # Set for each joint



'''
    GLOBAL OBJECTS

'''
rabbitmq_client = RabbitMQ_Client()
# Initialize threading event
end_event = threading.Event()
# client library 
url = "http://127.0.0.1:8080"

client = SYNC_APIClient(url)


def convert_to_floats(lst_str):
    # Check if the string is a valid list-like structure with numbers
    if re.fullmatch(r'\[([\d\.,\sEe\+\-]*)\]', lst_str):  # Matches patterns like '[1.0, 2.0, 0.5]'
        # Use ast.literal_eval to safely convert the string to a list
        try:
            return [float(x) for x in ast.literal_eval(lst_str)]  # Convert to floats
        except:
            return None
    else:
        return None  # Return None for invalid list-like strings


consumer_client = RabbitMQConsumerManager(rabbitmq_client=rabbitmq_client)

ipr = IPR()
ik_wrapper = IKPY_WRAPPER(urdf=urdf)
controller_manager = Robot_Control_Manager(ipr_object=ipr, ikpy_wrapper_object=ik_wrapper)

def on_task_feedback_callback(ch, method, properties, body):
    
    #pdb.set_trace()
    print(f" [x] Received {body}")
    ch.basic_ack(delivery_tag=method.delivery_tag)
    try: 
        json_data = json.loads(body.decode())
        json_data = json_data["response"]
        
        # Iterate through the data
        for task in json_data['TASK']:
            task['parameters'] = [
                convert_to_floats(param) if isinstance(param, str) else param
                for param in task['parameters']
            ]            
            
            if task["name"] == "calculate_inverse_kinematics":
                task["parameters"].pop()
                task["parameters"].pop()
            elif task["pass_returned_value_from"] != "":
                task["parameters"] = [controller_manager.get_return_value(task["pass_returned_value_from"])]
            controller_manager.execute_task(task["name"], task["parameters"])
            
            
    except json.JSONDecodeError:
        raise SystemError("Error: Invalid JSON format")
    

register_robot_doc = RegisterRobotRequest(**robot_capability_json)
response = client.post(
        "/robots/register",
        data=register_robot_doc.model_dump()
    )

register_robot_response = RegisterRobotResponse(**response)

print("response:", response)

register_task_doc = RegisterTaskRequest(**task_register_json)
register_task_doc.task.robot_id = register_robot_response.robot_id
response = client.post(
        "/task/register",
        data=register_task_doc.model_dump()
    )
register_task_response = RegisterTaskResponse(**response)
print("response:", response)


print("message to task request ")
json_env = {
    "environment": {
        "obstacles": [[]],
        "Position": [0.0, 0.0, 0.0,0.0,0.0,0.0]
    },
    "robot_id": "robot_0",
    "task_controller_type": "one_llm",
    "task_controller_model": "GPT4o",
    "task_id": "",

}
taskRequest = TaskRequest(**json_env)
taskRequest.robot_id = register_robot_response.robot_id
taskRequest.task_id = register_task_response.task_id
rabbitmq_client.send_message("task_request", message=taskRequest.model_dump())
consumer_client.start_consumer("task_feedback", callback=on_task_feedback_callback)



# initial_position = my_chain.inverse_kinematics_full(target_position=target_point)
# initial_position = np.array(initial_position)
# initial_position = initial_position[1:]
# initial_position[-2:] = [0.727475, -0.727475]


# print("number of links", len(my_chain.robot.links))
# print("initila position", initial_position)
# print("joints", len(initial_position))



#np.testing.assert_almost_equal(initial_position, target_orientation, decimal=5)



# ipr.grabObject(initial_position)
# ax2 = my_chain.plot_robot(initial_position)

while True:
    controller_manager.step()
    #Reset the event for the next iteration (if you need to reuse it)












