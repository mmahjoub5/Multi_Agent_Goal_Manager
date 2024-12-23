import os
#print("Current working directory:", os.getcwd())
import ikpy.chain
import numpy as np
import ikpy.utils.plot as plot_utils

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from ipr_worlds.controllers.ipr_cube_python.libraries.helpers import rotation_matrix_to_euler_angles
from ipr_worlds.controllers.ipr_cube_python.libraries.ikpy_wrapper import IKPY_WRAPPER
from ipr_worlds.controllers.ipr_cube_python.libraries.api_client import SYNC_APIClient, ASYNC_APIClient
from ipr_worlds.controllers.ipr_cube_python.json.robot_capability import robot_capability_json
import asyncio
from pydantic import BaseModel
from typing import List, Dict
import inspect
from ipr_worlds.shared.models import TaskRequest, SetGoalRequest
from ipr_worlds.shared.rabbitmq_manager import RabbitMQ_Client, RabbitMQConsumerManager

# my_chain = ikpy.chain.Chain.from_urdf_file("controllers/ipr_cube_python/IprHd6m180.urdf")
# urdf = "controllers/ipr_cube_python/IprHd6m180.urdf"
# my_chain =  IKPY_WRAPPER(urdf=urdf)




methods = [method for method, _ in inspect.getmembers(IKPY_WRAPPER, predicate=inspect.isfunction)]
methods = ["move arm to", "set motor positon", "position reached", "grab object"] + methods
rabbitmq_client = RabbitMQ_Client()


# client library 
url = "http://127.0.0.1:8000"

client = SYNC_APIClient(url)
json = { "environment": 
        {
            "robotLinks": [1,2,3],
            "goalPosition": [0,0,0],
            "NumberOfRobots": 3,
            "initialPositions": [0,10,1]
        },
        "tasks": methods,
        "task_controller_type": "autogen", # autogen, oneLLM, TWOLLM
        "robot_id": "0"

}

def on_task_feedback_callback(ch, method, properties, body):
    print(f" [x] Received {body}")

# env = TaskRequest(**json)

consumer_client = RabbitMQConsumerManager(rabbitmq_client=rabbitmq_client)

for i in range(2):
    goalRequest = SetGoalRequest(**robot_capability_json)
    print(goalRequest)
    response = client.post("/setGoal", data=goalRequest.model_dump())

    rabbitmq_client.send_message("task_request", message=json)
    consumer_client.start_consumer("task_feedback", callback=on_task_feedback_callback)










