import streamlit as st
import pandas as pd
import stripe
import csv
import hashlib
from data_fetching import load_data, get_sports_list, fetch_and_display_odds
from urllib.parse import quote  # Importer la fonction quote pour l'encodage d'URL

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

    # Écriture de tous les utilisateurs dans le fichier CSV (dans signup_page())
    return users

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

            # Actualiser la page pour appliquer les changements d'authentification
            st.experimental_rerun()
        else:
            st.error('Invalid username or password')

# Page principale après connexion
def main_page(username):
    st.title(f'Welcome to Bet Project, {username}!')

    # Bouton Log Out
    if st.button('Log Out'):
        st.session_state['authenticated'] = False
        st.session_state['username'] = None
        st.experimental_rerun()

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
        users = create_user(username, password, subscription)
        if not users:
            st.error('Username already exists. Please choose another one.')
            return
        
        st.success('Account created successfully. Redirecting to payment...')
        try:
            # Créer une session de paiement Stripe
            product_name = subscription
            product_price = 10.00 if subscription == 'Monthly Subscription' else 100.00

            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': product_name,
                        },
                        'unit_amount': int(product_price * 100),  # Stripe traite les montants en cents
                    },
                    'quantity': 1,
                }],
                mode='payment',
                
                success_url=f"https://betproject.streamlit.app?payment-success=1&username={quote(username)}",  # URL de succès du paiement
                cancel_url="https://betproject.streamlit.app?payment-cancel=1",    # URL d'annulation du paiement
            )
            st.markdown(f"[Complete your payment]({session.url})")
        except stripe.error.StripeError as e:
            st.error(f"Stripe error occurred: {e}")

# Page d'annulation de paiement
def cancel_page():
    st.title('Payment Cancelled')
    st.error('Your payment was cancelled. Please try again.')

# Page de succès de paiement
def success_page():
    username = st.experimental_get_query_params().get('username', [''])[0]
    if username:
        update_payment_status(username)
        st.session_state['authenticated'] = True
        st.session_state['username'] = username

        # Nettoyer les paramètres de la requête pour éviter le traitement multiple
        st.experimental_set_query_params()

        st.experimental_rerun()

    # Afficher un message de succès ou rediriger l'utilisateur
    st.success('Payment successful! Redirecting to the main page...')

    # Bouton Log Out
    if st.button('Log Out'):
        st.session_state['authenticated'] = False
        st.session_state['username'] = None
        st.experimental_rerun()

# Gestion des états de l'application
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
    st.session_state['username'] = None

# Vérifier si l'URL contient le paramètre de succès après le paiement
if st.experimental_get_query_params().get('payment-success'):
    success_page()  # Afficher la page de succès de paiement
elif st.session_state['authenticated']:
    main_page(st.session_state['username'])  # Afficher la page principale si l'utilisateur est authentifié
else:
    st.write('Welcome to Bet Project')
    st.write('Please select an option below:')
    option = st.selectbox('Choose an option:', ['Sign Up', 'Login'])

    if option == 'Sign Up':
        signup_page()  # Afficher la page de création de compte
    elif option == 'Login':
        login_page()  # Afficher la page de login
