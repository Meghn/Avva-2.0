# imports FastAPI's test client, which simulates HTTP requests 
# against your app without a real running server
from fastapi.testclient import TestClient
# imports the exact same app object you run with Uvicorn, 
# so the test exercises your real code
from app.main import app

# wraps your app in the fake-request client
client = TestClient(app)

# pytest automatically discovers and runs any function named 
# test_* in a file named test_*.py. No registration step needed
def test_health():
    # the arrange/act: makes a fake GET /health request
    response = client.get("/health")
    # the assert: fails the test loudly if the server didn't 
    # respond with success
    assert response.status_code == 200
    # checks the actual response body matches exactly what we expect
    assert response.json() == {"status": "ok"}
