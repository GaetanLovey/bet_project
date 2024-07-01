from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import pandas as pd

def initialize_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Exécuter Chrome en mode headless
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")

    service = ChromeService(executable_path='/path/to/chromedriver')  # Assurez-vous que le chemin est correct
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.execute_script("document.body.style.zoom='10%'")
    return driver

def open_main_page(driver, url):
    driver.get(url)
    try:
        accept_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, 'css-rymias'))
        )
        accept_button.click()
    except:
        print("Le bouton d'acceptation des cookies n'a pas été trouvé ou n'est pas cliquable.")

def scroll_and_load(driver, section_height=350, pause_time=2, max_sections=50):
    time.sleep(10)
    
    total_height = driver.execute_script("return document.body.scrollHeight")
    current_height = 0
    sections_scrolled = 0
    total_matches = 0
    matches_data = []
    
    while current_height < total_height and sections_scrolled < max_sections:
        driver.execute_script(f"window.scrollBy(0, {section_height});")
        time.sleep(pause_time)
        current_height += section_height
        
        wait_for_odds(driver)
        matches_data.extend(extract_data(driver))
        num_matches = len(matches_data) - total_matches
        total_matches += num_matches
        print(f"Nombre de matchs extraits jusqu'à présent : {total_matches}")
        
        sections_scrolled += 1
        
    df = pd.DataFrame(matches_data, columns=['match', 'win', 'draw', 'loose'])
    df.drop_duplicates(inplace=True)
    
    print("Scraping terminé !")
    return df

def wait_for_odds(driver):
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, '.css-1ni6zxi'))
    )

def extract_data(driver):
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    matches = soup.find_all(class_='css-khquoo')
    matches_data = []
    if matches:
        for match in matches:
            try:
                teams = match.find(class_='css-15hlj5j').get_text(strip=True)
                odds_elements = match.find_all(class_=lambda value: value and value.startswith('css-1ni6zxi'))
                if odds_elements and len(odds_elements) == 3:
                    odds_values = [odd.get_text(strip=True) for odd in odds_elements]
                    matches_data.append([teams] + odds_values)
            except Exception as e:
                print(f"Erreur lors de l'extraction des informations pour un match: {e}")
    return matches_data

def main():
    driver = initialize_driver()
    main_url = 'https://jeux.loro.ch/sports/hub/240?sport=FOOT'
    open_main_page(driver, main_url)
    df = scroll_and_load(driver)
    df.to_excel('loterie_romande.xlsx')
    driver.quit()
    return df

if __name__ == "__main__":
    main()
