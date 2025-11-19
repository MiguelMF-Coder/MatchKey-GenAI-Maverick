import time
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException, TimeoutException
from urllib.parse import urljoin
from bs4 import BeautifulSoup as bs
import undetected_chromedriver as uc
import pandas as pd



# --------------- FUNCIÓN PARA SCRAPPEAR ADZUNA Y SACAR TODAS LAS DESCRIPCIONES COMPLETAS --------------- #



PRIORITY_GROUPS = [
    ["/portal/impe/web/portadaEspecifica?channel="],
    ["identidad-y-mision"],
    ["valores"],
    ["saludo-rector"],
    ["historia"],
    ["mision", "misión", "vision", "visión", "misiones"],
    ["quienes-somos", "nosotros", "quienes", "about", "conoce"],
    ["planestrategico", "plan-estrategico", "plan_estrategico", "Plan-Estrategico"],
]

def open_main_menu(browser):
    """Hace hover sobre los elementos principales del menú para desplegar submenús"""
    try:
        nav_elements = browser.find_elements(By.CSS_SELECTOR, "nav")
        for nav in nav_elements:
            links = nav.find_elements(By.TAG_NAME, "a")
            for link in links:
                try:
                    ActionChains(browser).move_to_element(link).perform()
                except:
                    continue
        time.sleep(0.2)
    except:
        pass

def extract_links_from_elements(elements, base_url):
    "Extrae links sobre los elementos que le pasaremos (menú, footer o html)"
    links = set()
    for el in elements:
        try:
            href = el.get_attribute("href")
            if href:
                links.add(urljoin(base_url, href))
        except:
            continue
    return list(links)

def get_relevant_links(browser, urls):
    """
    Función principal. Para cada url aportada, tiene como objetivo devolver un link de interés(o None).
    Para ello, primero busca en el menú principal una de las keywords deseadas, luego en el footer y sino en el html 
    de la página principal.
    """
    universities = []

    for url in urls:
        chosen_link = None

        # Normalizar URL
        if not url.startswith("http"):
            url = "https://" + url.lstrip("http://").lstrip("https://")

        try:
            browser.set_page_load_timeout(15)
            browser.get(url)
            browser.implicitly_wait(1)
        except (WebDriverException, TimeoutException) as e:
            print(f"No se pudo cargar {url}: {e}")
            universities.append(None)
            continue

        # Buscar en menú principal
        open_main_menu(browser)
        try:
            nav_elements = browser.find_elements(By.CSS_SELECTOR, "nav a")
            links = extract_links_from_elements(nav_elements, url)
            for group in PRIORITY_GROUPS:
                matches = [l for l in links if any(k in l.lower() for k in group)]
                if matches:
                    chosen_link = matches[0]
                    break
        except:
            pass

        # Buscar en footer si no se encontró en el menú
        if not chosen_link:
            try:
                footer_elements = browser.find_elements(By.CSS_SELECTOR, "footer a")
                links = extract_links_from_elements(footer_elements, url)
                for group in PRIORITY_GROUPS:
                    matches = [l for l in links if any(k in l.lower() for k in group)]
                    if matches:
                        chosen_link = matches[0]
                        break
            except:
                pass

        # Buscar en todo el HTML como último recurso
        if not chosen_link:
            try:
                html = browser.page_source
                soup = bs(html, "html.parser")
                all_links = [urljoin(url, a["href"]) for a in soup.find_all("a", href=True)]
                for group in PRIORITY_GROUPS:
                    matches = [l for l in all_links if any(k in l.lower() for k in group)]
                    if matches:
                        chosen_link = matches[0]
                        break
            except:
                pass

        universities.append(chosen_link)
        time.sleep(0.1)  # espera mínima entre URLs

    return universities


# --------------- PROGRAMA PRINCIPAL --------------- #

browser = uc.Chrome()

df = pd.read_json("backend/app/services/scraping/universities/data/universities_raw.json", orient="records")

urls = urls = list(df["website"].unique())
universities_links = get_relevant_links(urls=urls, browser=browser)
    
browser.quit()


# --------------- GUARDAR CSV LIMPIO DE UNIVERSIDADES --------------- #
df_unis_raw = pd.DataFrame(universities_links)
df_unis_raw.to_csv("backend/app/services/scraping/universities/data/universities_links.csv", index=False)
print(f"CSV guardado en data/universities_links.csv")


# ---------------- OJO!!! SE HAN AÑADIDO A MANO LOS LINKS DE LAS UNIVERSIDADES QUE EL ALGORITMO --------------- #
# ---------------- NO HA PODIDO DETECTAR
