# backend/app/services/common/text_cleaning.py

import re
import unicodedata

def normalize_text(text: str) -> str:
    """
    Limpiar y normalizar texto:
    - quitar caracteres raros
    - normalizar acentos
    - pasar a minúsculas
    """
    if not text:
        return ""
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()
