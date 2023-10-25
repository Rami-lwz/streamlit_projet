import streamlit as st
import pandas as pd
from df_cleaner import get_cleaned_df
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import nltk
from nltk.corpus import stopwords
from pages.page_1__analyses_simples import Page_analyse_simples
import decorator_log

try: st.set_page_config(layout="wide") 
except: pass

class Page_wordcloud:
    
    def __init__(self, df):
        self.df = df
        self.custom_stop_words = set()

    def app(self, sidebar=True):
        st.title('Page d\'IA')  
        st.markdown("---")
        col1, col2 = st.columns([2, 1])
        self.df["Date de publication"] = pd.to_datetime(self.df["Date de publication"])
        
    
    
    def sidebar_sliders(self):
        min_date = self.df["Date de publication"].min().date()
        max_date = self.df["Date de publication"].max().date()
        
        st.sidebar.markdown("## Select a date range")
        date_range = st.sidebar.date_input(
            "Date range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
        )
        start_date, end_date = date_range

        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)

        mask = (self.df["Date de publication"] >= start_date) & (self.df["Date de publication"] <= end_date)
        self.df = self.df.loc[mask]
        
        
        # Filter for 'Nature juridique du rappel'
        unique_nature_juridique = self.df['Nature juridique du rappel'].unique()
        selected_nature_juridique = st.sidebar.multiselect('Select Nature juridique du rappel', options=unique_nature_juridique)

        # If specific 'Nature juridique' values are selected, filter the DataFrame
        if selected_nature_juridique:
            self.df = self.df[self.df['Nature juridique du rappel'].isin(selected_nature_juridique)]

        # Filter for 'Catégorie de produit'
        unique_categories = self.df['Catégorie de produit'].value_counts().index.unique()
        selected_categories = st.sidebar.multiselect('Select Catégorie de produit', options=unique_categories)
        if selected_categories:
            # Filter the DataFrame based on the selected categories
            self.df = self.df[self.df['Catégorie de produit'].isin(selected_categories)]

            # Get the unique subcategories after the filtering
            unique_sous_categories = self.df['Sous-catégorie de produit'].value_counts().index.unique()

            # Allow the user to select Subcategories
            selected_sous_categories = st.sidebar.multiselect('Select Sous Catégorie de produit', options=unique_sous_categories)

            if selected_sous_categories:
                # Filter the DataFrame based on the selected subcategories
                self.df = self.df[self.df['Sous-catégorie de produit'].isin(selected_sous_categories)]
        # If specific categories are selected, filter the DataFrame
        if selected_categories:
            self.df = self.df[self.df['Catégorie de produit'].isin(selected_categories)]

        # Filter for 'Nom de la marque du produit'
        unique_brands = self.df['Nom de la marque du produit'].value_counts().index.unique()
        selected_brands = st.sidebar.multiselect('Select Nom de la marque du produit', options=unique_brands)

        # If specific brands are selected, filter the DataFrame
        if selected_brands:
            self.df = self.df[self.df['Nom de la marque du produit'].isin(selected_brands)]

if __name__ == "__main__":
    p = Page_wordcloud(get_cleaned_df())
    print(p.custom_stop_words)
    p.app()