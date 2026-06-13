# Scraping, Values and Courses

## Purpose

Build the static or semi-static datasets that feed company culture, job data, university links and course recommendations.

## Source files detected

### Companies

- [backend/app/services/scraping/companies/companies_base_info.py](../../backend/app/services/scraping/companies/companies_base_info.py)
- [backend/app/services/scraping/companies/companies_raw_text.py](../../backend/app/services/scraping/companies/companies_raw_text.py)
- [backend/app/services/scraping/companies/companies_scrapper.py](../../backend/app/services/scraping/companies/companies_scrapper.py)
- [backend/app/services/scraping/companies/companies_values_scraper.py](../../backend/app/services/scraping/companies/companies_values_scraper.py)

### Courses

- [backend/app/services/scraping/courses/courses_scraper.py](../../backend/app/services/scraping/courses/courses_scraper.py)

### Jobs

- [backend/app/services/scraping/jobs/jobs_scraper.py](../../backend/app/services/scraping/jobs/jobs_scraper.py)
- [backend/app/services/scraping/jobs/descriptions_scraper.py](../../backend/app/services/scraping/jobs/descriptions_scraper.py)
- [backend/app/services/scraping/jobs/llm_scraper.py](../../backend/app/services/scraping/jobs/llm_scraper.py)

### Universities

- [backend/app/services/scraping/universities/universities_base_info.py](../../backend/app/services/scraping/universities/universities_base_info.py)
- [backend/app/services/scraping/universities/universities_raw_text.py](../../backend/app/services/scraping/universities/universities_raw_text.py)
- [backend/app/services/scraping/universities/universities_relevant_links.py](../../backend/app/services/scraping/universities/universities_relevant_links.py)

## Datasets detected

- Companies and links datasets.
- Job datasets generated from scraping.
- Course JSON datasets used by recommendations.
- University datasets and link-cleaning outputs.

## Current state

- Implemented as script-driven preprocessing.
- Some scripts are more like data pipelines than runtime modules.
- The repo contains real dataset outputs and some helper adapters.

## Notes

- Scraping and LLM-based extraction scripts are best treated as offline preparation tools.
- Some files contain hardcoded API keys or cloud prompts in the current snapshot; that should be revisited in later phases, but not changed here.
