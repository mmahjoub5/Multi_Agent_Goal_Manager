import os
#print("Current working directory:", os.getcwd())
import ikpy.chain
import numpy as np
import ikpy.utils.plot as plot_utils

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from ipr_worlds.controllers.ipr_cube_python.libraries.helpers import rotation_matrix_to_euler_angles
from ipr_worlds.controllers.ipr_cube_python.libraries.api_client import SYNC_APIClient, ASYNC_APIClient
from ipr_worlds.controllers.ipr_cube_python.json.robot_capability import robot_capability_json
from ipr_worlds.shared.models import TaskRequest, SetGoalRequest
from ipr_worlds.shared.rabbitmq_manager import RabbitMQ_Client, RabbitMQConsumerManager
from time import sleep
# my_chain = ikpy.chain.Chain.from_urdf_file("controllers/ipr_cube_python/IprHd6m180.urdf")
# urdf = "controllers/ipr_cube_python/IprHd6m180.urdf"
# my_chain =  IKPY_WRAPPER(urdf=urdf)
import threading
import json
import pdb


rabbitmq_client = RabbitMQ_Client()

# Initialize threading event
end_event = threading.Event()
# client library 
url = "http://127.0.0.1:8000"

client = SYNC_APIClient(url)
json_env = {
    "environment": {
        "obstacles": [[]],
        "Position": [0.0, 0.0, 0.0,0.0,0.0,0.0]
    },
    "robot_id": "robot_0",
    "task_controller_type": "one_llm",
    "task_controller_model": "GPT4o"

}

def on_task_feedback_callback(ch, method, properties, body):
    pdb.set_trace()
    print(f" [x] Received {body}")
    ch.basic_ack(delivery_tag=method.delivery_tag)
    try: 
        
        json_data = json.loads(body.decode())
        print(json_data["response"])
    except json.JSONDecodeError:
        raise SystemError("Error: Invalid JSON format")

    #json["environment"]["Position"] = [coord + 0.12 for coord in json["environment"]["Position"]]

    end_event.set()  # Signal the main loop that feedback is received
    
    # rabbitmq_client.send_message("task_request", message=json_env)



# env = TaskRequest(**json)

consumer_client = RabbitMQConsumerManager(rabbitmq_client=rabbitmq_client)
taskRequest = TaskRequest(**json_env)

goalRequest = SetGoalRequest(**robot_capability_json)
print(taskRequest)
response = client.post("/setGoal", data=goalRequest.model_dump())

rabbitmq_client.send_message("task_request", message=taskRequest.model_dump())
consumer_client.start_consumer("task_feedback", callback=on_task_feedback_callback)


while True:
    end_event.wait() 
    sleep(15)
    # Reset the event for the next iteration (if you need to reuse it)
    end_event.clear()

    









