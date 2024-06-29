import streamlit as st
import pandas as pd
st.title('Affichage de DataFrame avec Streamlit')

st.write("Voici un exemple de DataFrame :")
df = pd.read_excel('df.xlsx')
st.dataframe(df)  # Vous pouvez utiliser st.table(df) pour un affichage statique
