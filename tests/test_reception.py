import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_ping(client):
    response = client.get("/hello")
    assert response.status_code == 200
    assert response.get_json() == {"message": "Welcome to YoCah mechanics..."}


def test_transcribe(client):
    
    with open("tests/audio.txt", "r") as file:
        audio_b64 = file.read().strip()

    payload = {"audio": audio_b64}
    
    response = client.post("/transcribe", json=payload)
    print(response)
    assert response.status_code == 200
    data = response.get_json()
    assert "transcript" in data
    assert isinstance(data["transcript"], str)
    assert data["transcript"] ==  "Hello, I want to get my car serviced."
    
    
if __name__ == "__main__":
        
        import requests
        with open("tests/audio.txt", "r") as file:
            audio_b64 = file.read().strip()

        payload = {"audio": audio_b64}
        
        response = requests.post("http://localhost:5000/transcribe", json=payload)
        
        print(response)