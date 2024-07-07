import streamlit as st
import pandas as pd
import stripe
import hashlib
from data_fetching import load_data, get_sports_list, fetch_and_display_odds
from urllib.parse import quote
from models import User, SessionLocal, engine

# Clé API à utiliser pour les appels de données sportives
API_KEY = '9a58d306f402d400af1cafd8c6152ec9'

# Configuration de Stripe (utilisez votre clé API Stripe appropriée ici)
stripe.api_key = "sk_test_51PX1EnRpFgwyVO1as56l9TxhvladEkMOQ0nUHhj1ZKV0qnd8RcDBzrjK2Dx2zFzKNFM2ytTqGCFXYbhwHYsJroIn00JMlO6Cmb"

# Fonction pour créer un nouvel utilisateur
def create_user(username, password, subscription):
    db = SessionLocal()
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        return False  # L'utilisateur existe déjà

    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    new_user = User(username=username, password=hashed_password, subscription=subscription)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# Vérification des identifiants de connexion
def check_credentials(username, password):
    db = SessionLocal()
    user = db.query(User).filter(User.username == username).first()
    if user:
        hashed_password = user.password
        if hashed_password == hashlib.sha256(password.encode()).hexdigest():
            if user.paid:
                return True
            else:
                st.error('Payment not verified. Please complete the payment process.')
                return False
    return False

# Mise à jour de l'état de paiement
def update_payment_status(username):
    db = SessionLocal()
    user = db.query(User).filter(User.username == username).first()
    if user:
        user.paid = True
        db.commit()

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

            st.experimental_rerun()
        else:
            st.error('Invalid username, password, or payment not verified.')

# Page principale après connexion
def main_page(username):

    if st.button('Log Out'):
        st.session_state['authenticated'] = False
        st.session_state['username'] = None
        st.experimental_rerun()  # Recharger immédiatement la page après la déconnexion
        
    st.title(f'Welcome to Bet Project, {username}!')

    df, loterie_romande = load_data()
    
    st.subheader("Bookmaker above average:")
    st.dataframe(df)

    st.subheader("Loterie romande:")
    st.dataframe(loterie_romande)

    sports_list = get_sports_list(API_KEY)

    st.sidebar.title('Options')
    sport_keys = st.sidebar.multiselect('Choose sports:', sports_list)
    regions = st.sidebar.multiselect('Choose regions:', ['eu', 'uk', 'us', 'au'], default=['us'])
    markets = st.sidebar.selectbox('Choose markets:', ['h2h', 'spreads', 'totals'], index=0)
    odds_format = st.sidebar.selectbox('Choose odds format:', ['decimal', 'american'], index=0)
    date_format = st.sidebar.selectbox('Choose date format:', ['iso', 'unix'], index=0)

    if st.sidebar.button('Fetch'):
        fetch_and_display_odds(API_KEY, sport_keys, regions, markets, odds_format, date_format)

# Page de création de compte
def signup_page():
    st.title('Sign Up')

    username = st.text_input('Choose a username')
    password = st.text_input('Choose a password', type='password')
    subscription = st.selectbox('Choose a subscription', ['Monthly Subscription', 'Annual Subscription'])

    if st.button('Sign Up'):
        user = create_user(username, password, subscription)
        if not user:
            st.error('Username already exists. Please choose another one.')
            return
        
        st.success('Account created successfully. Redirecting to payment...')
        try:
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
                        'unit_amount': int(product_price * 100),
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=f"https://betproject.streamlit.app?payment-success=1&username={quote(username)}",
                cancel_url="https://betproject.streamlit.app?payment-cancel=1",
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
        st.experimental_set_query_params()
        st.experimental_rerun()

    st.success('Payment successful! Redirecting to the main page...')

# Gestion des états de l'application
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
    st.session_state['username'] = None

if st.experimental_get_query_params().get('payment-success'):
    success_page()
elif st.session_state['authenticated']:
    main_page(st.session_state['username'])
else:
    st.write('Welcome to Bet Project')
    st.write('Please select an option below:')
    option = st.selectbox('Choose an option:', ['Sign Up', 'Login'])

    if option == 'Sign Up':
        signup_page()
    elif option == 'Login':
        login_page()
