# backend/app/services/skills/skills_extractor.py

from pathlib import Path
import json
from ..common.text_cleaning import normalize_text

class SkillsExtractor:
    """
    Tool de extracción de skills.
    Pablo M implementará aquí TF-IDF, embeddings, reglas Must/Nice, etc.
    """

    def __init__(self):
        dict_path = Path(__file__).parent / "skills_dictionary.json"
        if dict_path.exists():
            self.dictionary = json.load(open(dict_path, "r", encoding="utf8"))
        else:
            self.dictionary = {}

    def extract(self, text: str) -> dict:
        """
        Por ahora: versión dummy.
        Más adelante:
        - usar diccionario
        - usar TF-IDF
        - usar embeddings
        """
        clean = normalize_text(text)
        skills = []

        for skill in self.dictionary.keys():
            if skill in clean:
                skills.append(skill)

        # Dummy: clasificar las dos primeras como must, el resto nice
        must_have = skills[:2]
        nice_to_have = skills[2:]

        return {
            "must_have": must_have,
            "nice_to_have": nice_to_have,
            "all_skills": skills
        }
