from pydantic import BaseModel, field_validator, field_validator, ValidationInfo, model_validator, Field
from typing import List, Dict, Optional, Union
import re 
from enum import Enum
from datetime import datetime

class STATUS(Enum):
    PENDING = "pending"
    IN_PROGRESS = "inprogress"
    COMPLETE = "complete"
    FAILED = "failed"

class TASK_TYPES(Enum):
    PICK_UP = "pickup"
    DROP = "drop"
    MOVE = "move"

class Enviroment(BaseModel):
    obstacles: Optional[List[List[Union[float,int]]]]
    Position:List[Union[float,int]]

# Define input structure
class TaskRequest(BaseModel):
    environment:Enviroment  # Details of the environment (e.g., objects, obstacles)
    robot_id: str
    task_controller_type: str # 
    task_controller_model: str 



# Define output structure
class TaskResponse(BaseModel):
    message: List[Dict[str,str]]



class TASK(BaseModel):
    tasks:List[str]
    name:str
    parameters:List[List[float]]
    pass_returned_value_from:str

    # #TODO: FIX SERIALIZER ERRORS THEN DEPLOY THIS
    @field_validator('name', mode='after')
    @classmethod
    def ensure_task_names(cls, value:str, info: ValidationInfo):
        tasks = info.data.get("tasks", [])
        if value not in tasks:
            raise ValueError(f"ensure_task_names failed because {value} not a valid name out of tasks")
        return value
    
   
    @field_validator('pass_returned_value_from',mode='after')
    @classmethod
    def ensure_pass_returned_value_from(cls, value, info: ValidationInfo):
        tasks = info.data.get("tasks", [])
        if value not in tasks and  value != "" and not None:
            raise ValueError(f"ensure_pass_returned_value_from {value} not a valid name out of tasks")
        return value
    

class TaskFeedback(BaseModel):
   TASK:List[TASK]

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
    target_position: Dict[str, float]  # {"x": 1.0, "y": 2.0, "z": 3.0},
    task_type: TASK_TYPES                 # Example: "move", "pickup", etc.
    additional_parameters: Optional[Dict[str, float]] = {}  # Any other task-specific parameters

# Model for robot locations (positions of robots at the start)
class RobotLocation(BaseModel):
    robot_id: Optional[str]
    position: List[float]  # Example: [x, y, z] coordinates of the robot



class RobotMetaData(BaseModel):
    # Meta data about the environment
    robot_type: str  # Type of robot(s) involved (e.g., 'robot_arm', 'mobile_robot')
    num_robots: int  # Number of robots involved in the task
    robot_capabilities: Optional[List[RobotCapabilities]] = None# Capabilities for each robot
    robot_locations: List[RobotLocation]  # Locations of the robots at the start of the task
    environment_constraints: Optional[Dict[str, str]] = {}  # Constraints for the environment (e.g., obstacles, boundaries)
    possible_tasks:List[Dict]


class GetAllRobotsResponse(BaseModel):
    robots: List[RobotMetaData]

class GetRobotByIDResponse(BaseModel):
    robot: RobotMetaData
    

# Main data model for the request body
class RegisterRobotRequest(BaseModel):
    robot: RobotMetaData

class DeleteRobotResponse(BaseModel):
    status: bool
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())  # Creation timestamp




class TaskMetaData(BaseModel):
    name: str
    robot_id:str
    goal_specifications: GoalSpecifications  # Specifications for the goal of the task
    task_controller_type: str # autogen, oneLLM, TWOLLM
    task_description: str  # Description of the task the client is asking


class RegisterTaskRequest(BaseModel):
    task: TaskMetaData

class RegisterTaskResponse(BaseModel):
    task_id:str
    status:STATUS
class ReachedGoalRequest(BaseModel):
    robot_id: str  # robot id 
    task_id: str # task id
    pass

class RegisterRobotResponse(BaseModel):
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())  # Creation timestamp
    robot_id: str


class GoalReachedRequest(BaseModel):
    robot_id: str
    task_id: str
    pass
class GoalReachedResponse(BaseModel):
    status: STATUS
    message: Optional[str] = None  # Additional info (optional)
    pass


