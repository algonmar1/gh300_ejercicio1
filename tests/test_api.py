"""
Tests for the FastAPI backend using Arrange-Act-Assert.
"""

import copy
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)


@pytest.fixture(autouse=True)
def restore_activities_state():
    original_activities = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original_activities)


class TestActivities:
    def test_get_activities_returns_expected_structure(self):
        # Arrange
        expected_activity = "Chess Club"

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert expected_activity in data
        assert "description" in data[expected_activity]
        assert "schedule" in data[expected_activity]
        assert "participants" in data[expected_activity]


class TestSignup:
    def test_signup_adds_participant(self):
        # Arrange
        activity_name = "Programming Class"
        email = "newstudent@mergington.edu"
        before_count = len(activities[activity_name]["participants"])

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert email in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == before_count + 1

    def test_signup_duplicate_returns_400(self):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"].lower()


class TestRemoveParticipant:
    def test_delete_participant_removes_entry(self):
        # Arrange
        activity_name = "Gym Class"
        email = "john@mergington.edu"
        assert email in activities[activity_name]["participants"]

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert email not in activities[activity_name]["participants"]

    def test_delete_nonexistent_participant_returns_404(self):
        # Arrange
        activity_name = "Tennis"
        email = "notfound@example.com"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert "participant not found" in response.json()["detail"].lower()
