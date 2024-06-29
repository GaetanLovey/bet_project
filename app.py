import streamlit as st
import pandas as pd
import requests

st.title('Interesting games')

# Lecture du DataFrame à partir d'un fichier Excel local (à remplacer par votre propre source de données)
df = pd.read_excel('df.xlsx')

# Affichage du DataFrame initial
st.write("Bookmaker above average :")
st.dataframe(df)

# Variables pour les URL de l'API et la clé API (remplacez par vos valeurs réelles)
API_KEY = '9a58d306f402d400af1cafd8c6152ec9'
SPORTS_URL = 'https://api.the-odds-api.com/v4/sports'
ODDS_URL = 'https://api.the-odds-api.com/v4/sports/{sport}/odds'

# Fonction pour récupérer la liste des sports disponibles depuis l'API
def get_sports_list(api_key):
    params = {'api_key': api_key}
    response = requests.get(SPORTS_URL, params=params)
    if response.status_code == 200:
        sports_data = response.json()
        sports_list = [sport['key'] for sport in sports_data]
        return sports_list
    else:
        st.error(f'Failed to fetch sports list: status_code {response.status_code}, response body {response.text}')
        return []

# Fonction pour récupérer et afficher les cotes en fonction des paramètres sélectionnés
def fetch_and_display_odds(sport_keys, regions, markets, odds_format, date_format):
    params = {
        'api_key': API_KEY,
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
            st.success(f'Sport: {sport_key}, Number of events: {len(odds_json)}')
            st.info(f'Remaining requests: {response.headers.get("x-requests-remaining")}')
            st.info(f'Used requests: {response.headers.get("x-requests-used")}')
        else:
            st.error(f'Failed to fetch odds for {sport_key}: status_code {response.status_code}, response body {response.text}')

    # Affichage des données récupérées sous forme de DataFrame ou autre visualisation
    if any(sport.startswith('soccer') for sport in sport_keys) and 'h2h' in markets:
        # Préparation des données pour les matchs de football avec le marché "h2h"
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
                win_odd = draw_odd = lose_odd = None

                for market in bookmaker['markets']:
                    if market['key'] == 'h2h':
                        for outcome in market['outcomes']:
                            if outcome['name'] == home_team:
                                win_odd = outcome['price']
                            elif outcome['name'] == away_team:
                                lose_odd = outcome['price']
                            elif outcome['name'] == 'Draw':
                                draw_odd = outcome['price']

                # Ajouter l'événement uniquement s'il n'existe pas déjà dans events
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
                        'Lose Odd': lose_odd
                    })

        columns = ['Event ID', 'Sport Key', 'Sport Title', 'Commence Time', 'Home Team', 'Away Team',
                   'Bookmaker Key', 'Bookmaker Title', 'Win Odd', 'Draw Odd', 'Lose Odd']
        if events:
            st.write(pd.DataFrame(events, columns=columns))
        else:
            st.warning('No data available for the selected criteria.')
    else:
        # Préparation des données pour d'autres sports
        events = []
        for event in all_odds:
            game_id = event['id']
            commence_time = event['commence_time']
            home_team = event['home_team']
            away_team = event['away_team']
            for bookmaker in event.get('bookmakers', []):
                bookmaker_key = bookmaker.get('key')
                last_update = bookmaker.get('last_update')

                for market in bookmaker.get('markets', []):
                    market_name = market.get('key')
                    for outcome in market.get('outcomes', []):
                        events.append({
                            'Game ID': game_id,
                            'Commence Time': commence_time,
                            'Home Team': home_team,
                            'Away Team': away_team,
                            'Bookmaker': bookmaker_key,
                            'Market': market_name,
                            'Outcome': outcome.get('name'),
                            'Odd': outcome.get('price'),
                            'Last Update': last_update
                        })

        if events:
            st.write(pd.DataFrame(events))
        else:
            st.warning('No data available for the selected criteria.')

# Récupération de la liste des sports disponibles
sports_list = get_sports_list(API_KEY)

# Utilisation de st.sidebar pour placer les widgets de sélection dans le sidebar
sport_keys = st.sidebar.multiselect('Choose sports:', sports_list)
regions = st.sidebar.multiselect('Choose regions:', ['eu', 'uk', 'us', 'au'], default=['us'])
markets = st.sidebar.selectbox('Choose markets:', ['h2h', 'spreads', 'totals'], index=0)
odds_format = st.sidebar.selectbox('Choose odds format:', ['decimal', 'american'], index=0)
date_format = st.sidebar.selectbox('Choose date format:', ['iso', 'unix'], index=0)

# Utilisation d'un bouton d'action dans le sidebar pour récupérer les données
fetch_button = st.sidebar.button('Fetch')

# Vérification si le bouton "Fetch" est cliqué
if fetch_button:
    # Appel de la fonction fetch_and_display_odds avec les paramètres sélectionnés
    fetch_and_display_odds(sport_keys, regions, markets, odds_format, date_format)
