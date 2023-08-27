import json
import pickle
import numpy as np
import os
from pydantic import BaseModel

config_path = os.path.join(os.path.dirname(__file__), "config.json")
with open(config_path, 'r') as file:
    config = json.load(file)


def load_model():
    """
        Load pretrained regression model.
    Returns:
            model (function): A function that takes apartment parameters input
        and returns a price (float).
    """
    model_path = config["trained_model"]
    regr_model = pickle.load(open(model_path, 'rb'))

    def model(apartment_params: BaseModel) -> float:
        """Send prediction of the trained model."""
        apartment_params = apartment_params.model_dump()
        district_part = [1.0 if (i + 1) == apartment_params["district"] else 0.0 for i in range(3)]
        del apartment_params["district"]
        apartment_params = np.concatenate((list(apartment_params.values()), district_part), axis=0)
        apartment_params = apartment_params.reshape((1, -1))
        prediction = regr_model.predict(apartment_params)[0]
        return prediction

    return model
