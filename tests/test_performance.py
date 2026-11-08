import statistics
import time

from starlette.testclient import TestClient

from api.main import app


PLACEMENT_INPUT = {
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


def test_repeated_prediction_performance():
    latencies = []
    with TestClient(app) as client:
        for _ in range(20):
            start = time.perf_counter()
            response = client.post("/predict", json=PLACEMENT_INPUT)
            latencies.append((time.perf_counter() - start) * 1000)
            assert response.status_code == 200
    assert len(latencies) == 20
    assert statistics.mean(latencies) > 0


def test_prediction_is_deterministic():
    with TestClient(app) as client:
        results = [
            client.post("/predict", json=PLACEMENT_INPUT).json()
            for _ in range(10)
        ]
    assert all(result == results[0] for result in results)


def test_batch_prediction_performance():
    with TestClient(app) as client:
        start = time.perf_counter()
        response = client.post(
            "/predict/batch",
            json={"customers": [PLACEMENT_INPUT] * 20},
        )
        elapsed = time.perf_counter() - start
    assert response.status_code == 200
    assert response.json()["count"] == 20
    assert elapsed > 0
