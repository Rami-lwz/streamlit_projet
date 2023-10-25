# main_app.py
import streamlit as st
import pandas as pd
import os
from df_cleaner import get_cleaned_df
from pages.page_analyses_simples import Page_analyse_simples
from pages.page_analyses_poussees import Page_analyse_poussee
try: st.set_page_config(layout="wide") 
except: pass

# Function to manage navigation
def app(df):
    st.title('Etude sur les Rappels de produits depuis 2018')
    st.markdown("Afficher la donnée") 
    selected_columns = st.multiselect("Colonnes", df.columns)
    # show df
    if selected_columns.__len__() > 0:
        df_show = df[selected_columns]
        st.dataframe(df_show)
       
# Run the app
if __name__ == "__main__":
    app(get_cleaned_df())