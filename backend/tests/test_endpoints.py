from fastapi.testclient import TestClient
from backend.app.main import app, ROBOTTABLE
from shared.models import *
from backend.tests.sample_json import sample_json_1
from backend.app.domain.documents import RobotDocument
client = TestClient(app)

def test_register_robot_sucess(mocker):
    mock_robot_doc:RobotDocument = mocker.MagicMock()
    
    mock_robot_doc.id = "robot_123"
    mock_robot_doc.robot = RobotMetaData(**sample_json_1["robot"])
    mocker.patch("backend.app.main.RobotDocument.create", return_value=mock_robot_doc)
    
     # Send the register robot request
    try:
        register_robot_doc = RegisterRobotRequest(**sample_json_1)
    except Exception as e:
        raise SyntaxError(f"{e}")
    response = client.post(
        "/robots/register",
        json=register_robot_doc.model_dump()
    )
    print(response)
    # Validate response
    assert response.status_code == 200
    data = response.json()

    # Assert returned response contains expected data
    assert data["robot_id"] == "robot_123"
    assert "timestamp" in data

    # Validate that the ROBOTTABLE cache is updated correctly
    assert "robot_123" in ROBOTTABLE
    assert ROBOTTABLE["robot_123"]["Doc"] == mock_robot_doc
    assert ROBOTTABLE["robot_123"]["Task_List"] == ["assemble", "inspect"]