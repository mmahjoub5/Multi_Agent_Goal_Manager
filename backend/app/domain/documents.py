from abc import ABC
from typing import Optional

from pydantic import UUID4, Field
from  backend.app.domain.base.nosql import NoSQLBaseDocument
from  shared.models import *
from datetime import datetime


class RobotDocument(NoSQLBaseDocument):
    class Settings:
        name = "Robot"
    # robot_type: str  # Type of robot(s) involved (e.g., 'robot_arm', 'mobile_robot')
    # num_robots: int  # Number of robots involved in the task
    # robot_capabilities: List[RobotCapabilities]  # Capabilities for each robot
    # robot_locations: List[RobotLocation]  # Locations of the robots at the start of the task
    # environment_constraints: Optional[Dict[str, str]] = {}  # Constraints for the environment (e.g., obstacles, boundaries)
    # possible_tasks:List[Dict]
    robot: RobotMetaData
    task_ids: List[str] = Field(default_factory=None)
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())  # Creation timestamp
    @classmethod
    def from_request(cls, request: RobotMetaData) -> "RobotDocument":
        return cls(**request.model_dump())
    
    @classmethod
    def get_or_create_from_request(cls, request: RobotMetaData) -> "RobotDocument":
        return cls.get_or_create(filter_doc=request.model_dump(exclude_unset=True))
    
    

class TaskDocument(NoSQLBaseDocument):
    class Settings:
        name = 'Task'
    task: TaskMetaData
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())  # Creation timestamp
    status: str  #"in-progress, complete, failed"
    response_ids: List[str] = Field(default_factory=None)

    @classmethod
    def from_request(cls, request: TaskMetaData) -> "TaskDocument":
        return cls(**request.model_dump())
    
    @classmethod
    def get_or_create_from_request(cls, request: TaskMetaData, ) -> "TaskDocument":
        return cls.get_or_create(filter_doc=request.model_dump(exclude_unset=True))
   
class ChatHistoryDocument(NoSQLBaseDocument):
    class Setting: 
        name = 'ChatHistory'
    task_id:str 
    reponse_text:List[Dict[str, str]]
    timestamp: str
    