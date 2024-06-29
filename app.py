# app.py

import streamlit as st
import pandas as pd
import requests
import stripe
import csv
import hashlib
import time
from data_fetching import load_data, get_sports_list, fetch_and_display_odds

# Clé API à utiliser pour les appels de données sportives
API_KEY = '9a58d306f402d400af1cafd8c6152ec9'

# Configuration de Stripe
stripe.api_key = "sk_test_51PX1EnRpFgwyVO1as56l9TxhvladEkMOQ0nUHhj1ZKV0qnd8RcDBzrjK2Dx2zFzKNFM2ytTqGCFXYbhwHYsJroIn00JMlO6Cmb"

# Chargement du fichier CSV des utilisateurs au démarrage de l'application
def load_users():
    users = {}
    try:
        with open('users.csv', 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                users[row['Username']] = {
                    'password': row['Password'],
                    'authenticated': False,
                    'subscription': row.get('Subscription', None),
                    'paid': row.get('Paid', False) == 'True'
                }
    except FileNotFoundError:
        # Créer le fichier users.csv s'il n'existe pas encore
        with open('users.csv', 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['Username', 'Password', 'Subscription', 'Paid'])
            writer.writeheader()

    return users

# Fonction pour créer un nouvel utilisateur
def create_user(username, password, subscription):
    users = load_users()  # Charger les utilisateurs actuels
    if username in users:
        return False  # L'utilisateur existe déjà

    # Hash du mot de passe pour le stockage sécurisé
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    users[username] = {'password': hashed_password, 'authenticated': False, 'subscription': subscription, 'paid': False}

    # Ajout de l'utilisateur au fichier CSV
    with open('users.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([username, hashed_password, subscription, 'False'])

    return True

# Vérification des identifiants de connexion
def check_credentials(username, password):
    users = load_users()  # Charger les utilisateurs actuels
    if username in users:
        hashed_password = users[username]['password']
        # Comparaison du mot de passe haché
        if hashed_password == hashlib.sha256(password.encode()).hexdigest():
            return True
    return False

# Page de connexion
def login_page():
    st.title('Login')

    username = st.text_input('Username')
    password = st.text_input('Password', type='password')

    if st.button('Login'):
        if check_credentials(username, password):
            st.session_state['authenticated'] = True
            st.session_state['username'] = username
            st.success('Login successful')
            st.experimental_rerun()  # Recharger la page pour appliquer l'état d'authentification
        else:
            st.error('Invalid username or password')

# Page principale après connexion
def main_page():
    st.title('Interesting games')

    # Ajout d'un bouton de déconnexion
    if st.button('Logout'):
        st.session_state['authenticated'] = False
        st.session_state['username'] = None
        st.session_state.sync()  # Synchroniser l'état de session
        st.experimental_rerun()  # Recharger la page pour appliquer l'état de déconnexion

    # Utilisation des fonctions importées pour charger et afficher les données
    df = load_data()
    st.write("Bookmaker above average :")
    st.dataframe(df)

    # Récupération de la liste des sports disponibles
    sports_list = get_sports_list(API_KEY)

    # Utilisation de st.sidebar pour placer les widgets de sélection dans le sidebar
    sport_keys = st.sidebar.multiselect('Choose sports:', sports_list)
    regions = st.sidebar.multiselect('Choose regions:', ['eu', 'uk', 'us', 'au'], default=['us'])
    markets = st.sidebar.selectbox('Choose markets:', ['h2h', 'spreads', 'totals'], index=0)
    odds_format = st.sidebar.selectbox('Choose odds format:', ['decimal', 'american'], index=0)
    date_format = st.sidebar.selectbox('Choose date format:', ['iso', 'unix'], index=0)

    # Appel de la fonction pour récupérer et afficher les cotes
    fetch_and_display_odds(API_KEY, sport_keys, regions, markets, odds_format, date_format)

# Gestion des états d'authentification
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = None

if st.session_state['authenticated']:
    main_page()
else:
    login_page()
