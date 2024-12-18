import os
#print("Current working directory:", os.getcwd())
import ikpy.chain
import numpy as np
import ikpy.utils.plot as plot_utils

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from libraries.helpers import rotation_matrix_to_euler_angles
from libraries.ikpy_wrapper import IKPY_WRAPPER
from libraries.api_client import SYNC_APIClient, ASYNC_APIClient
import asyncio
from pydantic import BaseModel
from typing import List, Dict

# my_chain = ikpy.chain.Chain.from_urdf_file("controllers/ipr_cube_python/IprHd6m180.urdf")
# urdf = "controllers/ipr_cube_python/IprHd6m180.urdf"
# my_chain =  IKPY_WRAPPER(urdf=urdf)


class Enviroment(BaseModel):
    robotLinks:List
    goalPosition: List
    NumberOfRobots:int
    initialPositions:List

class TaskRequest(BaseModel):
    environment:Enviroment  # Details of the environment (e.g., objects, obstacles)
           # End goal (e.g., cube position, robot target pose)


# client library 
url = "http://127.0.0.1:8000"

client = SYNC_APIClient(url)
json = { "environment": 
        {
            "robotLinks": [1,2,3],
            "goalPosition": [0,0,0],
            "NumberOfRobots": 3,
            "initialPositions": [0,10,1]
        }
}


env = TaskRequest(**json)
print(env.environment.robotLinks)
response = client.post("/taskPlaningTwoGPT", data=env.model_dump())
print(response)



# async_client = ASYNC_APIClient(url)


# async def call():
#     return await async_client.async_get("async")

# response = asyncio.run(call())
# print(response)





# target_point = [0, -.301, 0]

# initial_position = my_chain.inverse_kinematics_full(target_position=target_point)


# #ax1 = my_chain.plot_robot(target_point)
# print(initial_position)
# ax2 = my_chain.plot_robot(initial_position)

# plt.show()








