from pydantic import BaseModel
from typing import List, Dict, Optional, Union

class Enviroment(BaseModel):
    robotLinks:List
    goalPosition: List
    NumberOfRobots:int
    initialPositions:List


# Define input structure
class TaskRequest(BaseModel):
    environment:Enviroment  # Details of the environment (e.g., objects, obstacles)
    tasks: List
    task_controller_type: str # autogen, oneLLM, TWOLLM
    robot_id:str


# Define output structure
class TaskResponse(BaseModel):
    message: List[Dict[str,str]]


# 6DOF Joint Model
class Joints(BaseModel):
    name: str = None,
    type: str = None,
    bounds: List[Union[float, None]] = None,
    origin_translation: Optional[List[Union[float, None]]] = None,
    origin_orientation: Optional[List[Union[float, None]]] = None,
    rotation: Optional[List[Union[float, None]]] = None


# Model for robot capabilities (e.g., payload, speed, sensors)
class RobotCapabilities(BaseModel):
    payload_capacity: Optional[float] = None  # in kg, if applicable
    max_speed: Optional[float] = None         # in m/s
    sensors: Optional[List[str]] = []         # List of sensors available (e.g., "camera", "lidar")
    other_features: Optional[List[str]] = []  # Any other features
    joints: Optional[List[Joints]]              # Joint capabilities based on URDF of the robot 
# Model for the goal specifications
class GoalSpecifications(BaseModel):
    target_position: Optional[List[float]] = None  # Example: [x, y, z] for 3D space
    task_type: Optional[str] = None                # Example: "move", "pickup", etc.
    additional_parameters: Optional[Dict[str, str]] = {}  # Any other task-specific parameters

# Model for robot locations (positions of robots at the start)
class RobotLocation(BaseModel):
    robot_id: str
    position: List[float]  # Example: [x, y, z] coordinates of the robot

# Main data model for the request body
class SetGoalRequest(BaseModel):
    # Meta data about the environment
    robot_type: str  # Type of robot(s) involved (e.g., 'robot_arm', 'mobile_robot')
    num_robots: int  # Number of robots involved in the task
    robot_capabilities: List[RobotCapabilities]  # Capabilities for each robot
    robot_locations: List[RobotLocation]  # Locations of the robots at the start of the task
    task_description: str  # Description of the task the client is asking
    environment_constraints: Optional[Dict[str, str]] = {}  # Constraints for the environment (e.g., obstacles, boundaries)
    goal_specifications: GoalSpecifications  # Specifications for the goal of the task
    task_controller_type: str # autogen, oneLLM, TWOLLM

class SetGoalResponse(BaseModel):
    topicNames: List[str]
    time:str
    