# main_app.py
import streamlit as st
import pandas as pd
import os
from df_cleaner import get_cleaned_df
from pages.page_1__analyses_simples import Page_analyse_simples
try: st.set_page_config(layout="wide") 
except: pass

def app(df):
    st.title('Etude sur les Rappels de produits depuis 2018')
    st.markdown("Afficher la donnée") 

    selected_columns = st.multiselect("Colonnes", df.columns, default=df.columns.tolist())
    search_input = st.text_input("Barre de recherche", "", placeholder='🔍  |      Filtrer le DF ')
    if search_input:
        df = df[df[selected_columns].apply(lambda row: row.astype(str).str.contains(search_input, case=False).any(), axis=1)]

    st.metric(label="Nombre de produits observés", value=(df.shape[0]))
    col1, col2 = st.columns([7, 5])
    if len(selected_columns) == 0:
        with col1:  st.dataframe(df)
        with col2 : Page_analyse_simples(df).visu_images()
    if len(selected_columns) > 0:
        df_show = df[selected_columns]
        with col1 : st.dataframe(df_show)
        with col2 : Page_analyse_simples(df).visu_images()

if __name__ == "__main__":
    app(get_cleaned_df())