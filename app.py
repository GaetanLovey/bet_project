import streamlit as st
import pandas as pd
import stripe
import csv
import hashlib
from data_fetching import load_data, get_sports_list, fetch_and_display_odds

# Clé API à utiliser pour les appels de données sportives
API_KEY = '9a58d306f402d400af1cafd8c6152ec9'

# Configuration de Stripe (utilisez votre clé API Stripe appropriée ici)
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

    # Écriture de tous les utilisateurs dans le fichier CSV
    with open('users.csv', 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['Username', 'Password', 'Subscription', 'Paid'])
        writer.writeheader()
        for user, details in users.items():
            writer.writerow({
                'Username': user,
                'Password': details['password'],
                'Subscription': details['subscription'],
                'Paid': 'True' if details['paid'] else 'False'
            })

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

# Mise à jour de l'état de paiement dans le fichier CSV
def update_payment_status(username):
    users = load_users()
    if username in users:
        users[username]['paid'] = True
        with open('users.csv', 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['Username', 'Password', 'Subscription', 'Paid'])
            writer.writeheader()
            for user, details in users.items():
                writer.writerow({
                    'Username': user,
                    'Password': details['password'],
                    'Subscription': details['subscription'],
                    'Paid': 'True' if details['paid'] else 'False'
                })

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
            st.experimental_rerun()  # Recharger la page pour appliquer l'état mis à jour
        else:
            st.error('Invalid username or password')

# Page principale après connexion
def main_page():
    st.title('Interesting games')

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
    if st.sidebar.button('Fetch'):
        fetch_and_display_odds(API_KEY, sport_keys, regions, markets, odds_format, date_format)

# Page de création de compte
def signup_page():
    st.title('Sign Up')

    username = st.text_input('Choose a username')
    password = st.text_input('Choose a password', type='password')
    subscription = st.selectbox('Choose a subscription', ['Monthly Subscription', 'Annual Subscription'])

    if st.button('Sign Up'):
        if create_user(username, password, subscription):
            st.success('Account created successfully. Redirecting to login...')
            login_page()  # Rediriger vers la page de login après l'inscription réussie
        else:
            st.error('Username already exists. Please choose another one.')

# Gestion des états de l'application
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
    st.session_state['username'] = None

# Détermination de la page à afficher
if st.session_state['authenticated']:
    main_page()  # Afficher la page principale si l'utilisateur est authentifié
else:
    signup_page()  # Afficher la page de sign up si l'utilisateur n'est pas authentifié
    login_page()  # Afficher la page de login si l'utilisateur n'est pas authentifié
