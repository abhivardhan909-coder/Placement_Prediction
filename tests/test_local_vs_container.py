import json
import sys
from pathlib import Path
from urllib.request import Request, urlopen

from fastapi.testclient import TestClient


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from api.main import app


PAYLOAD = {
    "gender": "F",
    "ssc_p": 67.0,
    "ssc_b": "Others",
    "hsc_p": 91.0,
    "hsc_b": "Others",
    "hsc_s": "Commerce",
    "degree_p": 58.0,
    "degree_t": "Sci&Tech",
    "workex": "No",
    "etest_p": 55.0,
    "specialisation": "Mkt&HR",
    "mba_p": 58.8,
}


def call_container():
    data = json.dumps(PAYLOAD).encode("utf-8")

    request = Request(
        "http://localhost:8000/predict",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urlopen(request) as response:
        return json.loads(response.read().decode("utf-8"))


def test_local_and_container_predictions_match():
    with TestClient(app) as client:
        local_response = client.post("/predict", json=PAYLOAD)
    assert local_response.status_code == 200

    container_response = call_container()
    local_data = local_response.json()
    assert local_data["prediction"] == container_response["prediction"]
    assert local_data["predicted_status"] == container_response["predicted_status"]
    assert abs(
        local_data["placement_probability"] - container_response["placement_probability"]
    ) < 1e-10


def main():
    print("=" * 60)
    print("LOCAL VS CONTAINER PREDICTION CONSISTENCY")
    print("=" * 60)

    with TestClient(app) as client:
        local_response = client.post("/predict", json=PAYLOAD)

    container_response = call_container()

    print("\nLOCAL RESPONSE:")
    print(json.dumps(local_response.json(), indent=2))

    print("\nCONTAINER RESPONSE:")
    print(json.dumps(container_response, indent=2))

    local_data = local_response.json()

    local_prediction = local_data["prediction"]
    container_prediction = container_response["prediction"]

    local_probability = local_data["placement_probability"]
    container_probability = container_response["placement_probability"]

    print("\n" + "=" * 60)
    print("COMPARISON")
    print("=" * 60)

    print(f"Local prediction      : {local_prediction}")
    print(f"Container prediction : {container_prediction}")

    print(f"Local probability     : {local_probability}")
    print(f"Container probability: {container_probability}")

    prediction_match = local_prediction == container_prediction

    probability_match = abs(local_probability - container_probability) < 1e-10

    print(f"\nPrediction match      : {prediction_match}")
    print(f"Probability match     : {probability_match}")

    if prediction_match and probability_match:
        print("\n[SUCCESS] Local and container predictions are consistent.")
    else:
        print("\n[FAILURE] Local and container predictions differ.")
        raise AssertionError("Prediction consistency check failed.")


if __name__ == "__main__":
    main()
