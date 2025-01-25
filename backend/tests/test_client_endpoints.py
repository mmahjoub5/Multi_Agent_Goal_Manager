from fastapi.testclient import TestClient
from backend.app.main import app, ROBOTTABLE
from shared.models import *
from backend.tests.sample_json import sample_json_1, task_request
from backend.app.domain.documents import RobotDocument
from backend.app.domain.base.nosql import NoSQLBaseDocument
import pytest
from pydantic import ValidationError


client = TestClient(app)
NoSQLBaseDocument.configure_database_connection("test_database")


def test_RobotDoc_creation():
    robot_metadata= RobotMetaData(**sample_json_1["robot"])
    robot_doc = RobotDocument(robot=robot_metadata,
                              task_ids=["123","456"])
    assert robot_doc.id is not None
    assert robot_doc.timestamp is not None
    assert robot_doc.robot.robot_type == robot_metadata.robot_type

    assert robot_doc.task_ids == ["123","456"]

def test_RobotDoc_creation_missing_fields():
    with pytest.raises(ValidationError):
        robot_metadata= RobotMetaData(**sample_json_1["robot"])
        robot_metadata.robot_type = None
    
        robot_doc = RobotDocument(robot=RobotMetaData(**robot_metadata.model_dump()),
                              task_ids=["123","456"])



def test_register_robot_sucess():
    
    robot = RobotMetaData(**sample_json_1["robot"])
    
     # Send the register robot request
    try:
        register_robot_doc = RegisterRobotRequest(**sample_json_1)
    except Exception as e:
        raise SyntaxError(f"{e}")
    
    response = client.post(
        "/robots/register",
        json=register_robot_doc.model_dump()
    )
    # Validate response
    assert response.status_code == 200
    data = RegisterRobotResponse(**response.json())

    # Assert returned response contains expected data
    assert data.robot_id is not None 
    assert data.timestamp is not None

def test_register_get_robot():
    robot = RobotMetaData(**sample_json_1["robot"])
      # Send the register robot request
    try:
        register_robot_doc = RegisterRobotRequest(**sample_json_1)
    except Exception as e:
        raise SyntaxError(f"{e}")

    response = client.post(
        "/robots/register",
        json=register_robot_doc.model_dump()
    )

     # Validate response
    assert response.status_code == 200
    data = RegisterRobotResponse(**response.json())

    # Assert returned response contains expected data
    assert data.robot_id is not None 
    assert data.timestamp is not None

    get_response = client.get(
        f"/robots/{data.robot_id}",
    )

    assert get_response.status_code == 200
    get_robot_data = GetRobotByIDResponse(**get_response.json())

    assert get_robot_data.robot.num_robots == robot.num_robots
    assert get_robot_data.robot.robot_type == robot.robot_type
    

def test_get_robot_failure():
    robot_id = "1234"
    get_response = client.get(
        f"/robots/{robot_id}",
    )

    assert get_response.status_code == 400


def test_delete_robot():
    robot = RobotMetaData(**sample_json_1["robot"])
    # Send the register robot request
    try:
        register_robot_doc = RegisterRobotRequest(**sample_json_1)
    except Exception as e:
        raise SyntaxError(f"{e}")

    response = client.post(
        "/robots/register",
        json=register_robot_doc.model_dump()
    )

    # Validate response
    assert response.status_code == 200
    data = RegisterRobotResponse(**response.json())

    # Assert returned response contains expected data
    assert data.robot_id is not None 
    assert data.timestamp is not None

    delete_response = client.delete(
        f"/robots/{data.robot_id}",
    )

    assert delete_response.status_code == 200
    delete_data = DeleteRobotResponse(**delete_response.json())

    assert delete_data.status == True

    get_response = client.get(
        f"/robots/{data.robot_id}",
    )

    assert get_response.status_code == 400

def test_register_robot_meta_data_failure():
    try:
        register_robot = RegisterRobotRequest(**sample_json_1)
    except Exception as e:
        raise SyntaxError(f"{e}")
    
    register_robot.robot.num_robots = None 

    response = client.post(
        "/robots/register",
        json=register_robot.model_dump()
    )

    # Validate response
    assert response.status_code == 422


def test_register_robot_then_register_task():
    robot = RobotMetaData(**sample_json_1["robot"])
    # Send the register robot request
    try:
        register_robot_doc = RegisterRobotRequest(**sample_json_1)
    except Exception as e:
        raise SyntaxError(f"{e}")

    response = client.post(
        "/robots/register",
        json=register_robot_doc.model_dump()
    )

    assert response.status_code == 200
    robot_data = RegisterRobotResponse(**response.json())

    task = RegisterTaskRequest(**task_request)
    task.task.robot_id = str(robot_data.robot_id)

    response = client.post(
        "/task/register",
        json=task.model_dump()
    )

    assert response.status_code == 200
    task_data = RegisterTaskResponse(**response.json())

    assert task_data.task_id is not None
    assert task_data.status is not None
    assert task_data.status == STATUS.PENDING

def test_goal_reached():
    robot = RobotMetaData(**sample_json_1["robot"])
    # Send the register robot request
    try:
        register_robot_doc = RegisterRobotRequest(**sample_json_1)
    except Exception as e:
        raise SyntaxError(f"{e}")

    response = client.post(
        "/robots/register",
        json=register_robot_doc.model_dump()
    )

    assert response.status_code == 200
    robot_data = RegisterRobotResponse(**response.json())

    task = RegisterTaskRequest(**task_request)
    task.task.robot_id = str(robot_data.robot_id)

    response = client.post(
        "/task/register",
        json=task.model_dump()
    )

    assert response.status_code == 200
    task_data = RegisterTaskResponse(**response.json())

    assert task_data.task_id is not None
    assert task_data.status is not None
    assert task_data.status == STATUS.PENDING

    goal_reached = GoalReachedRequest(robot_id=str(robot_data.robot_id),
                                      task_id=task_data.task_id)
    response = client.post(
        "/task/goalReached",
        json=goal_reached.model_dump()
    )

    assert response.status_code == 200
    goal_reached_data = GoalReachedResponse(**response.json())

    assert goal_reached_data.status is not None
    assert goal_reached_data.status == STATUS.COMPLETE












