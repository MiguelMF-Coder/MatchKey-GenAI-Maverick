from bs4 import BeautifulSoup as bs
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
import pandas as pd



# --------------- FUNCIÓN PARA SCRAPPEAR ADZUNA Y SACAR TODAS LAS DESCRIPCIONES COMPLETAS --------------- #

def scrap_adzuna(url, browser):
    '''
    Function made to scrap each job offer from the webpage "adzuna".
    We are going to pass it to df_clean and make an apply for each offer in the dataset, 
    returning the full job description and creating a new column called description_full
    
    Args: 
        url (str): url of the webpage to scrape
        browser: initialized browser for webscrapping with uc
    
    Returns: 
        description_full (str): full description of the job
    '''
    
    browser.get(url)
    browser.implicitly_wait(0.5)
    
    try:
        browser.find_element(By.ID, "cookiescript_accept").click()
    except:
        pass
    
    html = browser.page_source
    soup = bs(html, "html.parser")
    description_full = soup.find('section', {"class": "adp-body"})
    
    if description_full:
        return description_full.text
    
    else:
        print(f"No se encontró la descripción para: {url}")
        return "" 
    
    
    
# --------------- CONFIGURACIÓN UC PARA EFICIENCIA TEMPORAL --------------- #

options = uc.ChromeOptions()
options.add_argument("--headless=new")
options.add_argument("--disable-gpu")
options.add_argument("--disable-extensions")
options.add_argument("--disable-default-apps")
options.add_argument("--blink-settings=imagesEnabled=false")
options.add_argument("--disable-sync")
options.add_argument("--disable-translate")
options.add_argument("--disable-features=IsolateOrigins,site-per-process")

caps = uc.ChromeOptions().to_capabilities()
caps["goog:loggingPrefs"] = {"performance": "ALL"}

browser = uc.Chrome(options=options, desired_capabilities=caps)

# Bloquear recursos pesados (IMÁGENES / CSS / FUENTES / VÍDEO)
browser.execute_cdp_cmd("Network.enable", {})
browser.execute_cdp_cmd("Network.setBlockedURLs", {
    "urls": [
        "*.png", "*.jpg", "*.jpeg", "*.gif", "*.webp",
        "*.svg", "*.css", "*.woff", "*.woff2",
        "*.mp4", "*.webm"
    ]
})


# --------------- PROGRAMA PRINCIPAL --------------- #

df = pd.read_csv("data/jobs_raw.csv")
df_clean = df.loc[df["redirect_url"].str.len() < 144].reset_index(drop=True)

urls = df_clean["redirect_url"]
descriptions = []

for url in urls:
    description_full = scrap_adzuna(url=url, browser=browser)
    descriptions.append(description_full)
    
browser.quit()


# --------------- GUARDAR CSV LIMPIO DE OFERTAS DE TABAJO --------------- #
df_clean["description_full"] = descriptions
df_clean.to_csv("data/jobs_descriptions.csv", index=False)
print(f"{len(df_clean)} ofertas guardadas en data/jobs_clean.csv")