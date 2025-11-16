# backend/app/services/ocr/document_parser.py

from ..common.text_cleaning import normalize_text

class DocumentParser:
    """
    Tool de OCR/lectura de documentos.
    Pablo M implementará aquí:
    - parse_pdf
    - parse_docx
    - parse_image
    """

    def parse_pdf(self, path: str) -> dict:
        # TODO: Implementar OCR y extracción real
        raw_text = "Texto de ejemplo extraído de PDF."
        clean_text = normalize_text(raw_text)
        return {
            "raw_text": raw_text,
            "clean_text": clean_text,
            "metadata": {"source_type": "pdf", "num_pages": 1}
        }

    def parse_docx(self, path: str) -> dict:
        raw_text = "Texto de ejemplo extraído de DOCX."
        clean_text = normalize_text(raw_text)
        return {
            "raw_text": raw_text,
            "clean_text": clean_text,
            "metadata": {"source_type": "docx"}
        }

    def parse_image(self, path: str) -> dict:
        raw_text = "Texto de ejemplo extraído de IMAGEN."
        clean_text = normalize_text(raw_text)
        return {
            "raw_text": raw_text,
            "clean_text": clean_text,
            "metadata": {"source_type": "image"}
        }
