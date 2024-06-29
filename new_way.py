import requests
import os

# Replace with your actual API key
API_KEY = '9a58d306f402d400af1cafd8c6152ec9'

# Step 1: Fetching in-season sports to confirm if UEFA Euro 2024 is available
sports_response = requests.get(
    'https://api.the-odds-api.com/v4/sports', 
    params={'api_key': API_KEY}
)

if sports_response.status_code == 200:
    sports_data = sports_response.json()
    print('List of in-season sports:')
    for sport in sports_data:
        print(f"{sport['key']}: {sport['title']}")
else:
    print(f'Failed to get sports: status_code {sports_response.status_code}, response body {sports_response.text}')

# Setting parameters for Soccer odds
SPORT = 'soccer_uefa_european_championship'  # Soccer sport key
REGIONS = 'eu'  # Focusing on EU and UK regions
MARKETS = 'h2h'  # Focusing on head-to-head market
ODDS_FORMAT = 'decimal'  # Using decimal format for odds
DATE_FORMAT = 'iso'  # Using ISO format for dates

# Step 2: Fetching Soccer odds
odds_response = requests.get(
    f'https://api.the-odds-api.com/v4/sports/{SPORT}/odds',
    params={
        'api_key': API_KEY,
        'regions': REGIONS,
        'markets': MARKETS,
        'oddsFormat': ODDS_FORMAT,
        'dateFormat': DATE_FORMAT,
    }
)


if odds_response.status_code == 200:
    odds_json = odds_response.json()
    print('Number of NBA events:', len(odds_json))
    print(odds_json) # This prints the fetched odds data
    # Check the usage quota
    print('Remaining requests', odds_response.headers['x-requests-remaining'])
    print('Used requests', odds_response.headers['x-requests-used'])
else:
    print(f'Failed to get odds: status_code {odds_response.status_code}, response body {odds_response.text}')



import pandas as pd


# Préparation des listes pour stocker les données extraites
events = []
for event in odds_json:
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

        # Ajout de chaque enregistrement à la liste des événements
        events.append([event_id, sport_key, sport_title, commence_time, home_team, away_team, 
                       bookmaker_key, bookmaker_title, win_odd, draw_odd, loose_odd])

# Création d'un DataFrame à partir de la liste des événements
columns = ['Event ID', 'Sport Key', 'Sport Title', 'Commence Time', 'Home Team', 'Away Team', 
           'Bookmaker Key', 'Bookmaker Title', 'Win Odd', 'Draw Odd', 'Loose Odd']
df = pd.DataFrame(events, columns=columns)

# Affichage du DataFrame
print(df)

df.to_excel('test.xlsx')



# 1. Analyser le marché afin de toruver les cotes intéressantes sur lesquelles parier 

# 2. Créer un site/ API afin de vendre les données sous forme d'abonnement 

# Créer un service pour analyser les cotes et founrir des conseils (paris arbitiraries comme valuebets ou surebets)

