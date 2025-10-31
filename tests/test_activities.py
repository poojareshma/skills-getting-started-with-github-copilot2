import pytest
from fastapi.testclient import TestClient

def test_get_activities(client: TestClient):
    response = client.get("/activities")
    assert response.status_code == 200
    activities = response.json()
    assert isinstance(activities, dict)
    # Check if we have the expected activity structure
    for name, details in activities.items():
        assert isinstance(name, str)
        assert "description" in details
        assert "schedule" in details
        assert "max_participants" in details
        assert "participants" in details
        assert isinstance(details["participants"], list)

def test_signup_activity(client: TestClient):
    # Get activities first to find an available one
    activities = client.get("/activities").json()
    activity_name = next(iter(activities.keys()))
    
    # Test successful signup
    response = client.post(f"/activities/{activity_name}/signup?email=test.student@mergington.edu")
    assert response.status_code == 200
    result = response.json()
    assert "message" in result
    
    # Verify participant was added
    activities = client.get("/activities").json()
    assert "test.student@mergington.edu" in activities[activity_name]["participants"]
    
    # Test duplicate signup
    response = client.post(f"/activities/{activity_name}/signup?email=test.student@mergington.edu")
    assert response.status_code == 400
    
def test_unregister_activity(client: TestClient):
    # First sign up a participant
    activities = client.get("/activities").json()
    activity_name = next(iter(activities.keys()))
    email = "test.unregister@mergington.edu"
    
    # Sign up the participant
    signup_response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert signup_response.status_code == 200  # Ensure signup succeeded
    
    # Test unregistration
    response = client.post(f"/activities/{activity_name}/unregister?email={email}")
    assert response.status_code == 200
    
    # Verify participant was removed
    activities = client.get("/activities").json()
    assert email not in activities[activity_name]["participants"]
    
    # Test unregistering non-existent participant
    response = client.post(f"/activities/{activity_name}/unregister?email=nonexistent@example.com")
    assert response.status_code == 400

def test_invalid_activity(client: TestClient):
    response = client.post("/activities/nonexistent/signup?email=test@example.com")
    assert response.status_code == 404
    
def test_invalid_email_format(client: TestClient):
    activities = client.get("/activities").json()
    activity_name = next(iter(activities.keys()))
    
    response = client.post(f"/activities/{activity_name}/signup?email=invalid_email")
    assert response.status_code == 422  # FastAPI's validation error status code