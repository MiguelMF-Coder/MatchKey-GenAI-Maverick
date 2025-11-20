import pandas as pd

# Leer el archivo .txt
about_us = "backend/app/services/scraping/companies/data/about_us.txt"
with open(about_us, "r", encoding="utf-8") as f:
    urls_list = [line.strip() for line in f if line.strip()]

# Convertir a DataFrame
df_urls = pd.DataFrame(urls_list, columns=["url_about_us"])

# Leer CSV con los datos de jobs
jobs = "backend/app/services/scraping/jobs/data/jobs_final.csv"
df_companies = pd.read_csv(jobs)
df_companies_filtered = pd.DataFrame(df_companies["company"].unique(), columns=["company"])

df_final = df_companies_filtered.merge(df_urls, right_index=True, left_index=True)

path = "backend/app/services/scraping/companies/data/companies_and_links.csv"
df_final.to_csv(path, index=False)

