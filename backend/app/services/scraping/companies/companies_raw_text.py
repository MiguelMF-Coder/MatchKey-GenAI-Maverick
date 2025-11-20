from bs4 import BeautifulSoup as bs
import undetected_chromedriver as uc
import re
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# --------------- FUNCIÓN PARA EXTRAER UUN TEXTO LIMPIO DE UNA PÁGINA WEB CUALQUIERA --------------- #

def clean_web_text(browser, url, wait_selector="body", timeout=10):
    """
    Extrae y limpia texto de una página web, esperando a que cargue el contenido principal.
    
    Args:
        browser: browser iniciado con uc
        url (str): URL de la página
        wait_selector (str): selector CSS del elemento que indica que la página cargó
        timeout (int): máximo tiempo a esperar en segundos
    
    Returns:
        str: texto limpio
    """
    browser.get(url)
    
    # Esperar a que el elemento principal esté presente
    try:
        WebDriverWait(browser, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, wait_selector))
        )
    except:
        print(f"Timeout al esperar {timeout}s por {wait_selector} en {url}")

    html = browser.page_source
    soup = bs(html, "html.parser")

    # eliminar scripts, estilos y noscript
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    text = soup.get_text(separator="\n", strip=True)

    # eliminar saltos de línea múltiples y espacios
    text = re.sub(r"\n\s*\n", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)

    # eliminar líneas irrelevantes típicas
    irrelevant_keywords = [
        "cookies", "aviso legal", "política de privacidad", "facebook", 
        "instagram", "twitter", "linkedin", "youtube", "flickr"
    ]
    lines = [line for line in text.split("\n") if not any(k in line.lower() for k in irrelevant_keywords)]
    
    cleaned_text = "\n".join(lines)
    return cleaned_text
    


# --------------- PROGRAMA PRINCIPAL --------------- #

options = uc.ChromeOptions()
# options.add_argument("--headless=new")
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


df = pd.read_csv("backend/app/services/scraping/companies/data/companies_and_links.csv")
df = df.dropna(subset=["url_about_us"])
urls = list(df["url_about_us"])

texts = []

for url in urls:
    
    text = clean_web_text(browser, url)
    texts.append(text)
    
browser.quit()


# --------------- GUARDAMOS EN CSV TODOS LOS TEXTOS --------------- #
df["clean_text"] = texts

df.to_csv("backend/app/services/scraping/companies/data/companies_pre_llm.csv", index=False, encoding="utf8")

print("Programa finalizado")