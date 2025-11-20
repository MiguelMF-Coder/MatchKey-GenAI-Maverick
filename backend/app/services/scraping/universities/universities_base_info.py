from bs4 import BeautifulSoup as bs
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
import pandas as pd
import json
import os

# ----------- FUNCIÓN PRINCIPAL DE SCRAPEO ----------- #

def scrap_unis_base(url, browser):
    '''
    Function made to scrap the base info of spanish universities
    
    Args: 
        url (str): url of the webpage to scrape
        browser: initialized browser for webscrapping with uc
    
    Returns: 
        universities (list of dicts): raw data of universities
    '''
    
    browser.get(url)
    browser.implicitly_wait(0.5)
    
    html = browser.page_source
    soup = bs(html, "html.parser")
    
    universities = []

    # Recorremos cada comunidad
    for comunidad_div in soup.find_all("div", class_="divComunidad"):
        # Para cada universidad dentro de la comunidad
        for uni_row in comunidad_div.find_all("tr", class_="rowComunidad"):
            name_td = uni_row.find("td", class_="col1")
            province_td = uni_row.find("td", class_="col3")
            website_td = uni_row.find("td", class_="col4")
            type_td = uni_row.find("td", class_="col2")

            name = name_td.get_text(strip=True) if name_td else ""
            province = province_td.get_text(strip=True) if province_td else ""
            website = website_td.find("a")["href"] if website_td and website_td.find("a") else ""
            uni_type = type_td.get_text(strip=True) if type_td else ""
            
            universities.append({
                "name": name,
                "website": website,
                "province": province,
                "type": uni_type
            })
            
    return universities


# ----------- PROGRAMA PRINCIPAL ----------- #

options = uc.ChromeOptions()
options.add_argument("--headless=new")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

browser = uc.Chrome(options=options)
url = "https://www.crue.org/universidades/" # Scrapeamos de este agregador de universidades españolas

universities = scrap_unis_base(url=url, browser=browser)

browser.quit()


# ----------- GUARDAR RESULTADOS ----------- #

output_dir = "backend/app/services/scraping/universities/data"
json_path = os.path.join(output_dir, "universities_raw.json")
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(universities, f, ensure_ascii=False, indent=4)




        
        
