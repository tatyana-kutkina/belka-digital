from clickhouse_driver import Client


def create_database(client: Client, name: str) -> None:
    query = f"CREATE DATABASE {name} ENGINE = Memory COMMENT 'The {name} database'"
    client.execute(query)


def create_table(client: Client, base_name: str, table_name: str, columns: str):
    client.execute(f"use {base_name}")
    client.execute(
        f"CREATE TABLE IF NOT EXISTS {base_name}.{table_name} ({columns})"
        f"ENGINE = MergeTree() ORDER BY id SETTINGS index_granularity=8192;"
    )


if __name__ == "__main__":
    client = Client(host='localhost', port='9000', settings={'use_numpy': True})
    base_name = "belka_digital"
    table_name = "apartment_database"
    columns = "id Int64, room_count Float64, floor Float64, total_floors Float64, price Float64, total_area Float64, live_area " \
              "Float64, kitchen_area Float64, district Float64, description String"
