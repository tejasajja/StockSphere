from fastapi.testclient import TestClient
import pytest
from ..main import app

client = TestClient(app)

def test_create_agent():
    agent_data = {
        "agent_id": 123456,
        "name": "John Doe",
        "contact": "john@example.com",
        "level": "Senior"
    }
    response = client.post("/agents/", json=agent_data)  # Ensure trailing slash if your API requires
    assert response.status_code == 200  # Adjust according to your API's actual response
    assert "agent_id" in response.json()  # Adjusting assertion based on your model

def test_get_agents():
    response = client.get("/agents/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_agent():
    # Use a known agent_id or set up the database before testing
    agent_id = 123456
    response = client.get(f"/agents/{agent_id}")
    assert response.status_code == 200
    # Adjusting check to ensure response includes the `agent_id`
    assert response.json()["agent_id"] == agent_id

def test_update_agent():
    # Use a known agent_id or create an agent as part of test setup
    agent_id = 123456
    updated_agent_data = {
        "name": "Mike Johnson Updated",
        "contact": "mike.updated@example.com",
        "level": "Mid-Level"
    }
    response = client.put(f"/agents/{agent_id}", json=updated_agent_data)
    assert response.status_code == 200
    updated_response = response.json()
    assert updated_response["name"] == updated_agent_data["name"]
    assert updated_response["contact"] == updated_agent_data["contact"]

def test_delete_agent():
    # Use a known agent_id or create an agent as part of test setup
    agent_id = 123456
    response = client.delete(f"/agents/{agent_id}")
    assert response.status_code == 200
    assert response.json() is True

    # Verify that the agent no longer exists
    response = client.get(f"/agents/{agent_id}")
    assert response.status_code == 404
