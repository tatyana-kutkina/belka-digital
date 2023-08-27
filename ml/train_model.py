import json
import pickle
import os
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
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    with open(config_path, 'r') as file:
        config = json.load(file)
    model_params = config["model_params"]
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    data_path = os.path.join(data_dir, 'train_test_data.csv')
    df = pd.read_csv(data_path, index_col=0)
    X, y = df.drop(["price"], axis=1), df["price"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42)
    train(X_train, y_train, model_params)
