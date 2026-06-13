# Document Parser

## Purpose

Convert CV files into structured candidate information that can be used by the backend and the frontend.

## Source file

- [backend/app/services/ocr/document_parser.py](../../backend/app/services/ocr/document_parser.py)

## Main classes and functions

- `CVReader`: reads PDF, DOCX and image files and returns cleaned text.
- `CVParser`: segments the text into sections and extracts contact info, skills, education and experience.
- `parse_cv_upload(upload_file)`: temporary-file wrapper used by the backend endpoint.

## Input / output

- Input: uploaded CV file.
- Output: structured dict with name, surname, location, contact, education, experience, skills and text preview.

## Dependencies

- `spacy`
- `unidecode`
- `pdfplumber`
- `pytesseract`
- `PIL`
- `pdf2image`
- `python-docx`

## Current state

- Implemented and real.
- The parser uses practical heuristics and OCR fallback paths.
- It is good enough for the current prototype, but still heuristic-based.

## Backend integration

- Used by `POST /candidates/{candidate_id}/parse_cv`.
- Updates candidate fields and candidate skills after parsing.
