""" from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Initialiser le driver Safari
driver = webdriver.Safari()

# URL de la page à scrapers
url = 'https://jeux.loro.ch/sports/hub/240?sport=FOOT'

# Ouvrir la page
driver.get(url)

# Attendre que le bouton "Accepter tous les cookies" soit chargé et cliquer dessus
try:
    accept_button = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.CLASS_NAME, 'css-rymias'))
    )
    accept_button.click()
except:
    print("Le bouton d'acceptation des cookies n'a pas été trouvé ou n'est pas cliquable.")

# Attendre que les éléments soient chargés (adapter la condition d'attente si nécessaire)
try:
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'css-khquoo'))
    )
    
    # Trouver les sections contenant les informations des cotes
    matches = driver.find_elements(By.CLASS_NAME, 'css-khquoo')
    
    # Vérifier si des matchs ont été trouvés

    if matches:
        for match in matches:
            teams = match.find_element(By.CLASS_NAME, 'css-15hlj5j').text.strip()  # Ajustez cette ligne selon la structure HTML réelle
            odds = match.find_elements(By.CLASS_NAME, 'css-gy9scf')  # Ajustez cette ligne selon la structure HTML réelle
            
            # Extraire les cotes pour chaque équipe
            odds_values = [odd.text.strip() for odd in odds]
            
            # Afficher les informations extraites
            print(f"Match: {teams}")
            print(f"Cotes: {odds_values}")
    else:
        print("Aucun match trouvé avec les sélecteurs fournis.")
finally:
    # Fermer le driver
    driver.quit()
 """




# https://medium.com/swlh/web-scraping-basics-scraping-a-betting-site-in-10-minutes-8e0529509848


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import pandas as pd 

# Initialiser le driver Safari
# driver = webdriver.Safari()

# URL de la page principale
# main_url = 'https://jeux.loro.ch/sports/hub/240?sport=FOOT'

# Ouvrir la page principale
# driver.get(main_url)

""" # Accepter les cookies si le bouton est présent
try:
    accept_button = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.CLASS_NAME, 'css-rymias'))
    )
    accept_button.click()
except Exception as e:
    print("Le bouton d'acceptation des cookies n'a pas été trouvé ou n'est pas cliquable:", e)

# Si un login est nécessaire, procéder au login
try:
    login_button = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.CLASS_NAME, 'login-btn'))
    )
    login_button.click()

    # Attendre que les champs de login soient présents
    username_field = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.ID, 'formEmailField'))
    )
    password_field = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.ID, 'formPasswordField'))
    )
    
    # Entrer les informations de login
    username_field.send_keys('gaetan_lovey@hotmail.com')
    password_field.send_keys('Ironside-1892@')
    
    # Cliquer sur le bouton de soumission
    submit_button = driver.find_element(By.ID, 'formLoginButton')
    submit_button.click()
    
except Exception as e:
    print("Le login n'a pas été possible ou n'est pas nécessaire:", e) """


def scroll_and_load(driver, section_height=350, pause_time=2, max_sections=200):
    # Attente de 10 secondes avant de commencer le défilement
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
        
        # Attendre que les cotes soient chargées
        wait_for_odds(driver)
        
        # Extraire les données des matchs
        matches_data.extend(extract_data(driver))
        num_matches = len(matches_data) - total_matches
        total_matches += num_matches
        print(f"Nombre de matchs extraits jusqu'à présent : {total_matches}")
        
        sections_scrolled += 1
        
    # Créer un DataFrame à partir des données extraites
    df = pd.DataFrame(matches_data, columns=['team_name_win', 'odds_win', 'odds_draw', 'team_name_lose', 'odds_lose'])
    
    # Supprimer les doublons
    df.drop_duplicates(inplace=True)
    
    print("Scraping terminé !")
    return df

def wait_for_odds(driver):
    # Attendre que les cotes soient visibles
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CLASS_NAME, 'm_bet-button__odds-text--current'))
    )

def extract_data(driver):
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    matches_data = []
    try:
        # Rechercher tous les éléments correspondant aux matchs
        matches = soup.find_all(class_=lambda value: value and value.startswith('m_bet-button__name ng-tns-c93-'))
        for i in range(0, len(matches), 3):
            try:
                # Extraire le nom de l'équipe gagnante
                team_name_win = matches[i].get_text(strip=True)
                
                # Extraire la cote de l'équipe gagnante
                odds_win = matches[i].find_next(class_='m_bet-button__odds-text--current').get_text(strip=True)
                
                # Extraire la cote du match nul
                odds_draw = matches[i+1].find_next(class_='m_bet-button__odds-text--current').get_text(strip=True)
                
                # Extraire le nom de l'équipe perdante
                team_name_lose = matches[i+2].get_text(strip=True)
                
                # Extraire la cote de l'équipe perdante
                odds_lose = matches[i+2].find_next(class_='m_bet-button__odds-text--current').get_text(strip=True)
                
                matches_data.append([team_name_win, odds_win, odds_draw, team_name_lose, odds_lose])
            except Exception as e:
                print(f"Erreur lors de l'extraction des informations pour un match: {e}")
    except Exception as e:
        print(f"Erreur lors de la recherche des éléments de match: {e}")
    return matches_data







# Initialise le driver
driver = webdriver.Chrome()

# Zoomer la page
driver.execute_script("document.body.style.zoom='10%'")

# URL de la page principale
main_url = 'https://www.swisslos.ch/fr/sporttip/parissportifs/prognostics/current/70'

# Ouvrir la page principale
driver.get(main_url)

# Exécuter le scraping
df = scroll_and_load(driver)


# Enregistrer le DataFrame dans un fichier Excel
df.to_excel('bet_bis.xlsx')

print(df)

# Fermer le driver
driver.quit()









