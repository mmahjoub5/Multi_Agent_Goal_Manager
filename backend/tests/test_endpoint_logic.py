from fastapi.testclient import TestClient
from backend.app.main import app, ROBOTTABLE
from shared.models import *
from backend.tests.sample_json import sample_json_1, task_request
from backend.app.domain.documents import RobotDocument
from backend.app.domain.base.nosql import NoSQLBaseDocument
import pytest
from pydantic import ValidationError

