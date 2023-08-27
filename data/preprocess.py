from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from clickhouse_driver import Client
import os
import json
import copy
import pandas as pd


def get_data(host: str, port: str, table_name: str, table_types: dict) -> pd.DataFrame:
    """Get raw data from database"""
    client = Client(host=host, port=port, settings={'use_numpy': True})
    result = client.execute(f"select * from {table_name}", with_column_types=True)
    columns = [column[0] for column in result[1]]
    data = result[0]
    df = pd.DataFrame(data=data, columns=columns)
    df = df.astype({})
    return df

def similar(text1: str, text2: str) -> bool:
    """Check if two texts are similar (describe the same apartments)."""
    vectorizer = TfidfVectorizer()
    text1_vector = vectorizer.fit_transform([text1])
    text2_vector = vectorizer.transform([text2])
    cosine_sim = cosine_similarity(text1_vector, text2_vector)
    return cosine_sim[0][0] > 0.8


def preprocess_data(raw_data: pd.DataFrame, path: str):
    """
    Check data for duplicates and missing values.
    Process categorical column 'district'.
    Then save preprocessed data to csv file.
    """
    df = copy.deepcopy(raw_data)
    ids = df["id"]
    df = df.dropna(how='any')
    df_origin = copy.deepcopy(df)
    df = df.drop(["description", "id"], axis=1)
    part = df.drop(["price"], axis=1)
    indexes = part[part.duplicated(
        subset=["room_count", "floor", "total_floors", "total_area", "live_area", "kitchen_area", "district"],
        keep=False)].index


    check = []
    for idx in indexes:
        if idx not in check:
            selected_row = part.loc[idx]
            matching_rows = part[part.apply(lambda row: row.equals(selected_row), axis=1)].index
            check.extend(matching_rows)
            match_df = df_origin.loc[matching_rows]
            for i in range(1, len(match_df)):
                descr1 = df_origin.loc[idx]["description"]
                descr2 = match_df.iloc[i]["description"]
                if similar(descr1, descr2):
                    df_origin.drop(match_df.index[i], inplace=True)
                    part.drop(match_df.index[i], inplace=True)
    df_origin = df_origin.reset_index(drop=True)
    df_origin.head()
    # fill live area column if it's 0
    mask = ((df["live_area"] == 0) & (df["kitchen_area"] != 0))
    df.loc[mask, "live_area"] = df.loc[mask, "total_area"] - df.loc[mask, "kitchen_area"]
    df = df_origin.drop(["description"], axis=1)
    df = df.drop(["id"], axis=1)
    df = pd.concat([df, pd.get_dummies(df["district"], prefix='district')], axis=1)
    df = df.drop(["district"], axis=1)

    df.to_csv(path)

if __name__ == "__main__":
    config_path = os.path.join(os.path.dirname(__file__), "data_config.json")
    with open(config_path, 'r') as file:
        config = json.load(file)
    table_types = config["table_types"]
    host = "localhost"
    port = "9000"
    table = 'belka_digital.apartment_database'
    raw_data = get_data(host, port, table, table_types)
    preprocessed_data = preprocess_data(raw_data, path="./train_test_data.csv")
