import json
import pickle
from sklearn.linear_model import BayesianRidge
from sklearn.model_selection import train_test_split
import pandas as pd


def train(X, y, model_params):
    """Train model and save to the disk."""
    model = BayesianRidge(**model_params)
    model.fit(X, y)
    filename = 'trained_model.sav'
    pickle.dump(model, open(filename, 'wb'))


if __name__ == "__main__":
    with open("/home/tatyana/PycharmProjects/belka-digital/ml/config.json", 'r') as file:
        config = json.load(file)
    model_params = config["model_params"]

    df = pd.read_csv("/home/tatyana/PycharmProjects/belka-digital/train_test_data.csv", index_col=0)
    X, y = df.drop(["price"], axis=1), df["price"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42)
    train(X_train, y_train, model_params)
