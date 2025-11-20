# backend/app/services/scraping/values_scraper.py

import json
from pathlib import Path

class ValuesAdapter:
    """
    Pablo: aquí puedes añadir scraping real si quieres,
    pero de momento usamos values_dataset.json.
    """

    def __init__(self):
        path = Path(__file__).parent / "values_dataset.json"
        self.data = json.load(open(path, "r", encoding="utf8"))

    def get_values(self, name: str):
        key = name.lower().replace(" ", "_")
        return self.data.get(key, {}).get("valores", [])
