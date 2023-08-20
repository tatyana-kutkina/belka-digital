import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
from typing import Optional, Union

import re


class Parser:
    """Class for parsing site 'citystar'."""

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

    def parse(self) -> pd.DataFrame:
        """Parse apartment information"""
        res = []
        for n in ['', 1, 2, 3, 4, 5]:
            df = pd.DataFrame()
            URL = f"http://citystar.ru/detal.htm?v_id=1&d=43&nm=%CE%E1%FA%FF%E2%EB%E5%ED%E8%FF+%2D+%CF%F0%EE%E4%E0%EC+%EA%E2%E0%F0%F2%E8%F0%F3+%E2+%E3%2E+%CC%E0%E3%ED%E8%F2%EE%E3%EE%F0%F1%EA%E5{n}"
            response = requests.get(URL)
            response.encoding = "cp1251"
            soup = bs(response.text, "html.parser")
            descriptions = soup.find_all("tr", class_=["tbb"])

            for i, description in enumerate(descriptions):
                if i == 59 or i == 63:
                    print(description.text)
                room_count = self.find_room_count(description.text)
                district = self.find_district(description.text)
                floor, total_floors = self.find_floor(description.text)
                total_area = self.find_total_area(description.text)
                price = self.find_price(description.text)
                new_row = {"room_count": room_count, "floor": floor, "total_floors": total_floors, "price": price, "area": total_area,
                           "district": district,
                           "description": description.text}
                df = pd.concat([df, pd.DataFrame(new_row, index=[0])], ignore_index=True)

        return df

if __name__ == "__main__":
    parser = Parser()
    df = parser.parse()
    df.to_csv("parsed_data.csv")