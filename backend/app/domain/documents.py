from abc import ABC
from typing import Optional

from pydantic import UUID4, Field
from ipr_worlds.backend.app.domain.base.nosql import NoSQLBaseDocument
from ipr_worlds.shared.models import *

from enum import StrEnum


class DataCategory(StrEnum):
    # PROMPT = "prompt"
    # QUERIES = "queries"

    # INSTRUCT_DATASET_SAMPLES = "instruct_dataset_samples"
    # INSTRUCT_DATASET = "instruct_dataset"
    # PREFERENCE_DATASET_SAMPLES = "preference_dataset_samples"
    # PREFERENCE_DATASET = "preference_dataset"

    # POSTS = "posts"
    # ARTICLES = "articles"
    # REPOSITORIES = "repositories"
    pass

class RobotDocument(NoSQLBaseDocument):
    class Settings:
        name = "Robot"
    robot_type: str  # Type of robot(s) involved (e.g., 'robot_arm', 'mobile_robot')
    num_robots: int  # Number of robots involved in the task
    robot_capabilities: List[RobotCapabilities]  # Capabilities for each robot
    robot_locations: List[RobotLocation]  # Locations of the robots at the start of the task
    task_description: str  # Description of the task the client is asking
    environment_constraints: Optional[Dict[str, str]] = {}  # Constraints for the environment (e.g., obstacles, boundaries)
    goal_specifications: GoalSpecifications  # Specifications for the goal of the task
    task_controller_type: str # autogen, oneLLM, TWOLLM

    @classmethod
    def from_request(cls, request: SetGoalRequest) -> "RobotDocument":
        return cls(**request.dict())

