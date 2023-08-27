import pytest
from ml.model import load_model
from app.app import ApartmentParams

apartment = ApartmentParams.model_validate({
    "room_count": 5,
    "floor": 1,
    "total_floor": 5,
    "total_area": 100,
    "live_area": 80,
    "kitchen_area": 10,
    "district": 1
})


@pytest.fixture(scope="function")
def model():
    return load_model()


def test_prediction(model):
    assert model(apartment)
