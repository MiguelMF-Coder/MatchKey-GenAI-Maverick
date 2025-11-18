from bs4 import BeautifulSoup as bs
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
import pandas as pd



# --------------- FUNCIÓN PARA SCRAPPEAR ADZUNA Y SACAR TODAS LAS DESCRIPCIONES COMPLETAS --------------- #

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
    browser.implicitly_wait(10)
    
    WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "divComunidad")))
    
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
            type_td = uni_row.find("td", class_="col5")

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


url = "https://www.crue.org/universidades/"
universities = scrap_unis_base(url=url, browser=browser)
    
browser.quit()


# --------------- GUARDAR CSV LIMPIO DE UNIVERSIDADES --------------- #
df_unis_raw = pd.DataFrame(universities)
df_unis_raw.to_json("backend/app/services/scraping/universities/data/universities_raw.json", orient="records", indent=4)
print(f"JSON guardado en data/universities_raw.json")