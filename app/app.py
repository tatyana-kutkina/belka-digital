from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from ml.model import load_model

app = FastAPI()


class ApartmentParams(BaseModel):
    room_count: int = Field(gt=0)
    floor: int = Field(gt=0)
    total_floor: int = Field(gt=0)
    total_area: float = Field(gt=0)
    live_area: float = Field(gt=0)
    kitchen_area: float = Field(gt=0)
    district: int = Field(gt=0)


class PriceResponse(BaseModel):
    apartment_params: ApartmentParams
    price: float


def correct_data(apartment: ApartmentParams):
    """Check some parameters of the apartment to be correct."""
    if apartment.district > 3:
        return False
    if apartment.live_area > apartment.total_area or apartment.kitchen_area > apartment.total_area:
        return False
    if apartment.floor > apartment.total_floor:
        return False
    return True


@app.get("/")
def index():
    return {"text": "Price Prediction"}


model = None


@app.on_event("startup")
def startup_event():
    global model
    model = load_model()


@app.post("/predict_price")
def predict_price(apartment: ApartmentParams):
    if not correct_data(apartment):
        raise HTTPException(status_code=400, detail="Invalid input data")
    price = model(apartment)
    response = PriceResponse(apartment_params=apartment, price=price)
    return response
