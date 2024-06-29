import streamlit as st
import pandas as pd
import requests
import ipywidgets as widgets
from IPython.display import display, clear_output
import pandas as pd

st.title('Interesting games')

st.write("Bookmaker above average :")
df = pd.read_excel('df.xlsx')
st.dataframe(df)  # Vous pouvez utiliser st.table(df) pour un affichage statique



# Remplacez ceci par votre clé API réelle
API_KEY = '9a58d306f402d400af1cafd8c6152ec9'

# URL de l'API pour récupérer la liste des sports disponibles
SPORTS_URL = 'https://api.the-odds-api.com/v4/sports'

# URL de l'API pour récupérer les cotes par sport sélectionné
ODDS_URL = 'https://api.the-odds-api.com/v4/sports/{sport}/odds'

# Variable globale pour stocker les DataFrames
global_odds_df = pd.DataFrame()

# Fonction pour récupérer la liste des sports depuis l'API
def get_sports_list(api_key):
    params = {'api_key': api_key}
    response = requests.get(SPORTS_URL, params=params)
    if response.status_code == 200:
        sports_data = response.json()
        sports_list = [sport['key'] for sport in sports_data]
        return sports_list
    else:
        print(f'Failed to fetch sports list: status_code {response.status_code}, response body {response.text}')
        return []

def fetch_odds(button):
    global global_odds_df
    
    sport_keys = sport_select.value
    regions = regions_select.value
    markets = markets_dropdown.value
    odds_format = odds_format_dropdown.value
    date_format = date_format_dropdown.value
    api_key = API_KEY
    
    params = {
        'api_key': api_key,
        'regions': ','.join(regions),
        'markets': markets,
        'oddsFormat': odds_format,
        'dateFormat': date_format,
    }

    all_odds = []
    for sport_key in sport_keys:
        url = ODDS_URL.format(sport=sport_key)
        response = requests.get(url, params=params)
        if response.status_code == 200:
            odds_json = response.json()
            all_odds.extend(odds_json)
            print(f'Sport: {sport_key}, Number of events: {len(odds_json)}')
            # Vérifie le quota d'utilisation
            print('Remaining requests:', response.headers['x-requests-remaining'])
            print('Used requests:', response.headers['x-requests-used'])
        else:
            print(f'Failed to fetch odds for {sport_key}: status_code {response.status_code}, response body {response.text}')
    
    # Nettoyage des résultats précédents
    with output:
        clear_output(wait=True)

        if any(sport.startswith('soccer') for sport in sport_keys) and 'h2h' in markets:
            # Préparation des données pour le DataFrame si le sport commence par "soccer" et le marché est "h2h"
            events = []
            for event in all_odds:
                event_id = event['id']
                sport_key = event['sport_key']
                sport_title = event['sport_title']
                commence_time = event['commence_time']
                home_team = event['home_team']
                away_team = event['away_team']

                for bookmaker in event['bookmakers']:
                    bookmaker_key = bookmaker['key']
                    bookmaker_title = bookmaker['title']
                    win_odd = draw_odd = loose_odd = None

                    for market in bookmaker['markets']:
                        if market['key'] == 'h2h':
                            for outcome in market['outcomes']:
                                if outcome['name'] == home_team:
                                    win_odd = outcome['price']
                                elif outcome['name'] == away_team:
                                    loose_odd = outcome['price']
                                elif outcome['name'] == 'Draw':
                                    draw_odd = outcome['price']

                    # Ajouter uniquement si l'événement n'existe pas encore dans events
                    if (event_id, bookmaker_key) not in [(e['Event ID'], e['Bookmaker Key']) for e in events]:
                        events.append({
                            'Event ID': event_id,
                            'Sport Key': sport_key,
                            'Sport Title': sport_title,
                            'Commence Time': commence_time,
                            'Home Team': home_team,
                            'Away Team': away_team,
                            'Bookmaker Key': bookmaker_key,
                            'Bookmaker Title': bookmaker_title,
                            'Win Odd': win_odd,
                            'Draw Odd': draw_odd,
                            'Loose Odd': loose_odd
                        })

            columns = ['Event ID', 'Sport Key', 'Sport Title', 'Commence Time', 'Home Team', 'Away Team',
                       'Bookmaker Key', 'Bookmaker Title', 'Win Odd', 'Draw Odd', 'Loose Odd']
            df = pd.DataFrame(events, columns=columns)
            display(df)
        else:
            # Préparation des données pour les autres sports
            events = {}
            for event in all_odds:
                game_id = event.get('id')
                commence_time = event.get('commence_time')
                home_team = event['home_team']
                away_team = event['away_team']
                for bookmaker in event.get('bookmakers', []):
                    bookmaker_key = bookmaker.get('key')
                    last_update = bookmaker.get('last_update')

                    
                    if (game_id, bookmaker_key) not in events:
                        events[(game_id, bookmaker_key)] = {
                            'game_id': game_id,
                            'commence_time': commence_time,
                            'bookmaker': bookmaker_key,
                            'last_update': last_update,
                            'home_team': home_team,
                            'away_team': away_team,
                            'market': None,
                            'label_1': None,
                            'odd_1': None,
                            'point_1': None,
                            'label_2': None,
                            'odd_2': None,
                            'point_2': None,
                            'odd_draw': None
                        }
                    for market in bookmaker.get('markets', []):
                        for i, outcome in enumerate(market.get('outcomes', [])):
                            if i == 0:
                                # events[(game_id, bookmaker_key)]['home_team'] = outcome.get('home_team')
                                events[(game_id, bookmaker_key)]['label_1'] = outcome.get('name')
                                events[(game_id, bookmaker_key)]['odd_1'] = outcome.get('price')
                                events[(game_id, bookmaker_key)]['point_1'] = outcome.get('point')
                            elif i == 1:
                                # events[(game_id, bookmaker_key)]['away_team'] = outcome.get('away_team')
                                events[(game_id, bookmaker_key)]['label_2'] = outcome.get('name')
                                events[(game_id, bookmaker_key)]['odd_2'] = outcome.get('price')
                                events[(game_id, bookmaker_key)]['point_2'] = outcome.get('point')
                            elif i == 2:
                                events[(game_id, bookmaker_key)]['odd_draw'] = outcome.get('price')

            # Convertir le dictionnaire en liste pour créer le DataFrame
            events_list = list(events.values())
            columns = ['game_id', 'commence_time', 'bookmaker', 'last_update', 'home_team', 'away_team',
                       'market', 'label_1', 'odd_1', 'point_1', 'label_2', 'odd_2', 'point_2', 'odd_draw']
            df = pd.DataFrame(events_list, columns=columns)
            display(df)
    
    # Mise à jour de la variable globale
    global_odds_df = df

# Récupération de la liste des sports disponibles
sports_list = get_sports_list(API_KEY)

# Création de la liste déroulante des sports avec sélection multiple
sport_select = widgets.SelectMultiple(
    options=sports_list,
    description='Choose sports:',
    disabled=False,
)

# Création de la liste déroulante pour les régions avec sélection multiple
regions_select = widgets.SelectMultiple(
    options=['eu', 'uk', 'us', 'au'],
    value=['us'],
    description='Choose regions:',
    disabled=False,
)

# Création de la liste déroulante pour les marchés (markets)
markets_dropdown = widgets.Dropdown(
    options=['h2h', 'spreads', 'totals'],
    value='h2h',
    description='Choose markets:',
    disabled=False,
)

# Création de la liste déroulante pour le format des cotes (odds format)
odds_format_dropdown = widgets.Dropdown(
    options=['decimal', 'american'],
    value='decimal',
    description='Choose odds format:',
    disabled=False,
)

# Création de la liste déroulante pour le format de date
date_format_dropdown = widgets.Dropdown(
    options=['iso', 'unix'],
    value='iso',
    description='Choose date format:',
    disabled=False,
)

# Création du bouton Fetch
fetch_button = widgets.Button(
    description='Fetch',
    disabled=False,
    button_style='',  # 'success', 'info', 'warning', 'danger' or ''
    tooltip='Fetch odds data',
    icon='check'  # (FontAwesome names without the `fa-` prefix)
)

# Attacher l'événement de clic du bouton à la fonction fetch_odds
fetch_button.on_click(fetch_odds)

# Utilisation d'un Output pour encapsuler les widgets et les résultats
output = widgets.Output()

# Afficher les widgets dans le notebook
display(widgets.VBox([sport_select, regions_select, markets_dropdown, odds_format_dropdown, date_format_dropdown, fetch_button, output]))
