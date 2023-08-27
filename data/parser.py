from typing import Optional, Union
import re

import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import numpy as np

from clickhouse_driver import Client


class Parser:
    """Class for parsing site 'citystar.ru'."""

    regions = ["Ленинский", "Орджоникидзевский", "Правобережный", "Орджоникидзевский (Левый берег)",
               "Ленинский (левый берег)"]
    districts_labels = {
        "ленинск": 1,
        "орджоникидзевск": 2,
        "правобережн": 3
    }
    rooms = {
        "однокомнатн": 1,
        "двухкомнатн": 2,
        "трехкомнатн": 3,
        "трёхкомнатн": 3,
        "четырехкомнатн": 4,
        "четырёхкомнатн": 4

    }

    def __init__(self, links=None):
        if links is None:
            self.links = [
                "http://citystar.ru/detal.htm?sT=1&v_id=1&d=43&ag=&nm=%CE%E1%FA%FF%E2%EB%E5%ED%E8%FF+%2D+%CF%F0%EE%E4%E0%EC+%EA%E2%E0%F0%F2%E8%F0%F3+%E2+%E3%2E+%CC%E0%E3%ED%E8%F2%EE%E3%EE%F0%F1%EA%E5&pS=100",
                "http://citystar.ru/detal.htm?sT=1&v_id=1&d=43&ag=&nm=%CE%E1%FA%FF%E2%EB%E5%ED%E8%FF+%2D+%CF%F0%EE%E4%E0%EC+%EA%E2%E0%F0%F2%E8%F0%F3+%E2+%E3%2E+%CC%E0%E3%ED%E8%F2%EE%E3%EE%F0%F1%EA%E5&pS=100&pN=2",
                "http://citystar.ru/detal.htm?sT=1&v_id=1&d=43&ag=&nm=%CE%E1%FA%FF%E2%EB%E5%ED%E8%FF+%2D+%CF%F0%EE%E4%E0%EC+%EA%E2%E0%F0%F2%E8%F0%F3+%E2+%E3%2E+%CC%E0%E3%ED%E8%F2%EE%E3%EE%F0%F1%EA%E5&pS=100&pN=3",
                "http://citystar.ru/detal.htm?sT=1&v_id=1&d=43&ag=&nm=%CE%E1%FA%FF%E2%EB%E5%ED%E8%FF+%2D+%CF%F0%EE%E4%E0%EC+%EA%E2%E0%F0%F2%E8%F0%F3+%E2+%E3%2E+%CC%E0%E3%ED%E8%F2%EE%E3%EE%F0%F1%EA%E5&pS=100&pN=4",
                "http://citystar.ru/detal.htm?sT=1&v_id=1&d=43&ag=&nm=%CE%E1%FA%FF%E2%EB%E5%ED%E8%FF+%2D+%CF%F0%EE%E4%E0%EC+%EA%E2%E0%F0%F2%E8%F0%F3+%E2+%E3%2E+%CC%E0%E3%ED%E8%F2%EE%E3%EE%F0%F1%EA%E5&pS=100&pN=5"
            ]
        else:
            self.links = links

    def find_room_count(self, text: str) -> Optional[int]:
        """
        Get info how many rooms does the apartment have.

        If description has conflicting information about room number,
        it's set to None.
        """
        pattern = r"\b(\w+комнатн\w+)"
        matches = re.findall(pattern, text, flags=re.IGNORECASE)
        room_count = []
        for tag in matches:
            tag = tag.lower()[:-2]
            if tag in self.rooms.keys():
                room_count.append(self.rooms[tag])
        if len(room_count) == 0:
            room_count = None
        elif len(set(room_count)) != 1:
            room_count = None
        else:
            room_count = room_count[0]
        return room_count

    def find_district(self, text: str) -> Optional[str]:
        """Get information about district where the apartment is."""
        district_matches = []
        district_match1 = re.search(r'\b(\S+)\s+районе\b', text)
        district_matches.append(district_match1.group(1) if district_match1 else None)

        district_match2 = re.search(r'\b(\S+)\s+район\b', text)
        district_matches.append(district_match2.group(1) if district_match2 else None)
        district = None
        for dis in district_matches:
            if dis is not None:
                district = self.districts_labels.get(dis.lower()[:-2], None)
        return district

    def find_total_area(self, text: str) -> Optional[float]:
        """Get total area of the apartment."""
        area_match = re.search(r'Общая площадь - (\d+\.\d+) кв\.м\.', text)
        area = float(area_match.group(1)) if area_match else None
        return area

    def find_live_area(self, text: str) -> Optional[float]:
        """Get live area of the apartment."""
        area_match = re.search(r'жилая площадь - (\d+\.\d+) кв\.м\.', text)
        area = float(area_match.group(1)) if area_match else None
        return area

    def find_kitchen_area(self, text: str) -> Optional[float]:
        """Get area of the kitchen."""
        area_match = re.search(r'кухня - (\d+\.\d+) кв\.м\.', text)
        area = float(area_match.group(1)) if area_match else None
        return area

    def find_floor(self, text: str) -> Union[tuple[int, int], tuple[None, None]]:
        """
        Get total number of floors in the house
        and get apartment floor.
        """
        floor_match = re.search(r'этаж (\d+/\d+)', text)
        floor = floor_match.group(1) if floor_match else None
        if floor is not None:
            total_floors = int(floor[-1])
            floor = int(floor[0])
            return floor, total_floors
        else:
            return None, None

    def find_price(self, text: str) -> Optional[int]:
        """Get price of the apartment."""
        price_match = re.search(r'Цена - (\d+)', text)
        price = int(price_match.group(1)) if price_match else None
        return price

    def parse(self, client: Client, table_name: str):
        """Parse apartment information and add it to clickhouse database"""
        k = 0
        for URL in self.links:
            try:
                response = requests.get(URL, timeout=30)
                if response.status_code == 200:
                    response.encoding = "cp1251"
                    soup = bs(response.text, "html.parser")
                    descriptions = soup.find_all("tr", class_=["tbb"])

                    for description in descriptions:
                        room_count = self.find_room_count(description.text)
                        district = self.find_district(description.text)
                        floor, total_floors = self.find_floor(description.text)
                        total_area = self.find_total_area(description.text)
                        live_area = self.find_live_area(description.text)
                        kitchen_area = self.find_kitchen_area(description.text)
                        price = self.find_price(description.text)
                        new_row = {"id": k, "room_count": room_count, "floor": floor, "total_floors": total_floors,
                                   "price": price,
                                   "total_area": total_area,
                                   "live_area": live_area,
                                   "kitchen_area": kitchen_area,
                                   "district": district,
                                   "description": description.text.replace("'", "")}
                        values = [str(value) if pd.notna(value) else np.nan for value in new_row.values()]
                        values = [f"'{value}'" if isinstance(value, str) else str(value) for value in values]
                        query = f"INSERT INTO {table_name} ({', '.join(new_row.keys())}) VALUES ({', '.join(values)})"
                        client.execute(query)
                        k += 1
            except requests.exceptions.Timeout:
                print("Timed out")


if __name__ == "__main__":
    parser = Parser()
    client = Client(host='localhost', port='9000', settings={'use_numpy': True})
    table_name = "belka_digital.apartment_database"
    parser.parse(client=client, table_name=table_name)
