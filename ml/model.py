from sklearn.linear_model import BayesianRidge
from sklearn.model_selection import train_test_split
import pandas as pd
import json
import numpy as np
from pydantic import BaseModel


# TODO: get data from database

df = pd.read_csv("/home/tatyana/PycharmProjects/belka-digital/train_test_data.csv", index_col=0)
X, y = df.drop(["price"], axis=1), df["price"]
X_train, X_test, y_train, y_test = train_test_split(X, y)
with open("/home/tatyana/PycharmProjects/belka-digital/ml/model_params.json", 'r') as file:
    model_params = json.load(file)


def correct_apartment(apartent_params):
    """Check that all fields are filled correctly."""
    return True


def load_model():
    """
        Init and fit regression model.
    Returns:
            model (function): A function that takes apartment parameters input (json)
        and returns a price (float).
    """
    regr_model = BayesianRidge(**model_params)
    regr_model.fit(X_train, y_train)

    def model(apartment_params: BaseModel) -> float:
        # TODO: run preprocessing
        # TODO: check for correct input data
        #  and send some message if apartemtn parameters are not correct

        """Send prediction of the trained model."""
        apartment_params = apartment_params.model_dump()
        if correct_apartment(apartment_params):
            district_part = [1.0 if (i + 1) == apartment_params["district"] else 0.0 for i in range(3)]
            del apartment_params["district"]
            apartment_params = np.concatenate((list(apartment_params.values()), district_part), axis=0)
            apartment_params = apartment_params.reshape((1, -1))
            prediction = regr_model.predict(apartment_params)[0]
            return prediction
        else:
            return -1000

    return model

# class ApartmentParams(BaseModel):
#     room_count: int
#     floor: int
#     total_floor: int
#     total_area: float
#     live_area: float
#     kitchen_area: float
#     district: int
#
# if __name__ == "__main__":
#     d = {
#         "room_count": 5,
#         "floor": 1,
#         "total_floor": 5,
#         "total_area": 100,
#         "live_area": 80,
#         "kitchen_area": 10,
#         "district": 1
#     }
#     tmp = ApartmentParams.model_validate(d)
#     model = load_model()
#     print(model(tmp))
