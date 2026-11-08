import pytest
from starlette.testclient import TestClient

from api.main import app


VALID_PLACEMENT = {
    "gender": "M",
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


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_metadata(client):
    response = client.get("/metadata")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "Placement Prediction API"
    assert data["model_loaded"] is True
    assert data["preprocessor_loaded"] is True


def test_valid_prediction(client):
    response = client.post("/predict", json=VALID_PLACEMENT)
    assert response.status_code == 200
    data = response.json()
    assert data["prediction"] in (0, 1)
    assert data["predicted_status"] in ("Placed", "Not Placed")
    assert 0.0 <= data["placement_probability"] <= 1.0
    assert (data["prediction"] == 1) == (data["predicted_status"] == "Placed")


def test_rejects_invalid_category(client):
    payload = VALID_PLACEMENT | {"gender": "Unknown"}
    response = client.post("/predict", json=payload)
    assert response.status_code == 422
    assert response.json()["message"] == "Request validation failed"


def test_rejects_out_of_range_score(client):
    payload = VALID_PLACEMENT | {"ssc_p": 105}
    response = client.post("/predict", json=payload)
    assert response.status_code == 422


def test_batch_prediction(client):
    payload = {"customers": [VALID_PLACEMENT, VALID_PLACEMENT | {"gender": "F"}]}
    response = client.post("/predict/batch", json=payload)
    assert response.status_code == 200
    assert response.json()["count"] == 2
    assert all(
        0.0 <= result["placement_probability"] <= 1.0
        for result in response.json()["predictions"]
    )
