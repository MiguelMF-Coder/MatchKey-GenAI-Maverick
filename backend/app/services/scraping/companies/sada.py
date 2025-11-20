import pandas as pd

df = pd.read_csv("backend/app/services/scraping/jobs/data/jobs_final.csv")
companies = sorted(df["company"].dropna().unique())

print(f"Total empresas únicas: {len(companies)}")
for c in companies:
    print(c)

