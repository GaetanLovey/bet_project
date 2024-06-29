# data_fetching.py

import streamlit as st
import pandas as pd
import requests

# Lecture du DataFrame à partir d'un fichier Excel local (à remplacer par votre propre source de données)
def load_data():
    df = pd.read_excel('df.xlsx')
    return df

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
def fetch_and_display_odds(api_key, sport_keys, regions, markets, odds_format, date_format):
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
        st.write("Other odds :")
        for sport in all_odds:
            st.write(sport)
