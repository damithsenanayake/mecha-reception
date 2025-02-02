import pytest
from app import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_scheduler(client):
    payload = {
        "name": "Test User",
        "email": "damithsenanayake90@mail.com",
        "car_make": "Mitsubishi",
        "car_model": "Lancer",
        "service_date": "13-01-2026",
        
    }

    response = client.post("/schedule_service", json=payload)
    assert response.status_code == 201

if __name__ == "__main__":
    
    import requests
    payload = {
        "name": "Test User",
        "email": "damithsenanayake90@mail.com",
        "car_make": "Mitsubishi",
        "car_model": "Lancer",
        "service_date": "13-01-2026",        
    }
    response = requests.post("http://localhost:5000/schedule_service", json = payload)
    
    print(response.status_code)
    print(response.error)