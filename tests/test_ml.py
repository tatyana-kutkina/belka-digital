import pytest
from ml.model import load_model


@pytest.fixture(scope="function")
def model():
    # Load the model once for each test function
    return load_model()


def test_prediction(model):
    apartment = {
        "room_count": 5,
        "floor": 1,
        "total_floor": 5,
        "total_area": 100,
        "live_area": 80,
        "kitchen_area": 10,
        "district": 1
    }
    assert model(apartment)
