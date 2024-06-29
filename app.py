import streamlit as st
import pandas as pd
st.title('Interesting games')

st.write("Bookmaker above average :")
df = pd.read_excel('df.xlsx')
st.dataframe(df)  # Vous pouvez utiliser st.table(df) pour un affichage statique
