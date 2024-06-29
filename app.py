import streamlit as st
import pandas as pd
import stripe

# Configuration de Stripe
stripe.api_key = "sk_test_YOUR_SECRET_KEY"  # Remplacez par votre clé secrète Stripe

# Configuration de la connexion (modifiez ces valeurs)
USERNAME = "user"
PASSWORD = "password"

# Liste de tous les utilisateurs enregistrés (simulé ici pour un exemple)
registered_users = {
    "user": {
        "password": "password",
        "subscribed": False
    }
}

# Fonction de vérification des identifiants
def check_credentials(username, password):
    return username in registered_users and registered_users[username]["password"] == password

# Fonction pour inscrire un nouvel utilisateur
def register_user(username, password):
    registered_users[username] = {
        "password": password,
        "subscribed": False
    }

# Interface utilisateur Streamlit
st.title('Subscription Service')

if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if not st.session_state['authenticated']:
    st.title('Login or Register')

    # Formulaire de login
    username = st.text_input('Username')
    password = st.text_input('Password', type='password')

    login_button = st.button('Login')
    register_button = st.button('Register')

    if login_button:
        if check_credentials(username, password):
            st.session_state['authenticated'] = True
            st.success('Login successful')
        else:
            st.error('Invalid username or password')

    if register_button:
        new_username = st.text_input('New Username')
        new_password = st.text_input('New Password', type='password')

        if st.button('Register'):
            register_user(new_username, new_password)
            st.success(f'User {new_username} registered successfully! Please login.')

    if st.session_state['authenticated']:
        st.title('Subscribe to our service')

        product_name = "Monthly Subscription"
        product_price = 10.00  # Prix en USD

        if st.button(f"Pay ${product_price} for {product_name}"):
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
                success_url="https://your-success-url.com",
                cancel_url="https://your-cancel-url.com",
            )
            st.markdown(f"[Complete your payment]({session.url})")

else:
    st.title('Interesting games')

    # Ajout d'un bouton de déconnexion
    if st.button('Logout'):
        st.session_state['authenticated'] = False

    # Ajout d'un formulaire de paiement Stripe pour les utilisateurs connectés
    st.subheader("Subscribe to our service")

    product_name = "Monthly Subscription"
    product_price = 10.00  # Prix en USD

    if st.button(f"Pay ${product_price} for {product_name}"):
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
            success_url="https://your-success-url.com",
            cancel_url="https://your-cancel-url.com",
        )
        st.markdown(f"[Complete your payment]({session.url})")
