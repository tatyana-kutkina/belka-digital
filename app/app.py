from fastapi import FastAPI
from pydantic import BaseModel
from ml.model import load_model

app = FastAPI()


class ApartmentParams(BaseModel):
    room_count: int
    floor: int
    total_floor: int
    total_area: float
    live_area: float
    kitchen_area: float
    district: int


class PriceResponse(BaseModel):
    apartment_params: ApartmentParams
    price: float


@app.get("/")
def index():
    return {"text": "Price Prediction"}


model = None


# Register the function to run during startup
@app.on_event("startup")
def startup_event():
    global model
    model = load_model()


@app.post("/predict_price")
def predict_price(apartment: ApartmentParams):
    predict_price = model(apartment)
    response = PriceResponse(apartment_params=apartment, price=predict_price)
    return response
