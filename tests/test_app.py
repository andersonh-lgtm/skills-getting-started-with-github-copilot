from copy import deepcopy
from pathlib import Path
from urllib.parse import quote
import sys

import pytest
from fastapi.testclient import TestClient

# Ensure the repository root is on sys.path so `src` can be imported when running tests directly.
repo_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo_root))

from src.app import app, activities as activities_data

client = TestClient(app)
initial_activities = deepcopy(activities_data)


@pytest.fixture(autouse=True)
def reset_activities():
    activities_data.clear()
    activities_data.update(deepcopy(initial_activities))
    yield


def test_root_redirect():
    # Arrange

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_expected_data():
    # Arrange

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert data["Chess Club"]["description"].startswith("Learn strategies")
    assert data["Chess Club"]["participants"] == ["michael@mergington.edu", "daniel@mergington.edu"]


def test_signup_adds_participant():
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    # Act
    response = client.post(f"/activities/{quote(activity_name)}/signup?email={quote(email, safe='')}")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert email in activities_data[activity_name]["participants"]


def test_duplicate_signup_returns_bad_request():
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.post(f"/activities/{quote(activity_name)}/signup?email={quote(email, safe='')}")

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_remove_participant():
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.delete(f"/activities/{quote(activity_name)}/participants/{quote(email, safe='')}")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from {activity_name}"
    assert email not in activities_data[activity_name]["participants"]
