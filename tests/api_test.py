import sys
from pathlib import Path
import numpy as np
import importlib.util
import pytest
from fastapi.testclient import TestClient

# Add the project root to the PYTHONPATH
file = Path(__file__).resolve()
root = file.parents[1]  # Adjust this as necessary
sys.path.append(str(root))

# Dynamically import main.py
main_path = root / 'app' / 'main.py'
spec = importlib.util.spec_from_file_location("main", main_path)
main = importlib.util.module_from_spec(spec)
sys.modules["main"] = main
spec.loader.exec_module(main)

# Create a TestClient instance
client = TestClient(main.app)

def test_health():
    response = client.get("/api/v1/health")  # Ensure this path matches the one in main.py
    assert response.status_code == 200
    assert isinstance(response.json(), dict)
    assert "name" in response.json()
    assert "api_version" in response.json()
    assert "model_version" in response.json()
    
def test_predict_valid_input():
    input_data = {
        "inputs": [
            {
                "dteday": "2012-11-05",
                "season": "winter",
                "hr": "6am",
                "holiday": "No",
                "weekday": "Mon",
                "workingday": "Yes",
                "weathersit": "Mist",
                "temp": 6.1,
                "atemp": 3.0014,
                "hum": 49.0,
                "windspeed": 19.0012,
                "casual": 4,
                "registered": 135
            }
        ]
    }
    expected_status = 200
    expected_response = {
        "errors": None,
        "version": "0.0.1",
        "predictions":  86.24635745
    }
    
    response = client.post("/api/v1/predict", json=input_data)
    assert response.status_code == expected_status
    response_json = response.json()
    assert "predictions" in response_json
    assert response_json["predictions"] == pytest.approx(expected_response["predictions"], rel=1e-2)
    assert response_json["version"] == expected_response["version"]
    assert response_json["errors"] == expected_response["errors"]
