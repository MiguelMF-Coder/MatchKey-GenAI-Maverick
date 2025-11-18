# backend/app/services/scraping/courses_scraper.py

import json
from pathlib import Path

class CoursesAdapter:
    """
    Pablo: aquí luego puedes añadir scraping real,
    ahora tiramos del JSON estático.
    """

    def __init__(self):
        path = Path(__file__).parent / "courses_dataset.json"
        self.courses = json.load(open(path, "r", encoding="utf8"))

    def get_courses_for_skill(self, skill: str):
        skill = skill.lower()
        return [c for c in self.courses if c["skill"] == skill]
    
    def import_vacantes_json(self, json_path: str):
        path = Path(json_path)
        self.courses = json.load(open(path, "r", encoding="utf8"))


