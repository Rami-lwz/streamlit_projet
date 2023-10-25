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

class Page_analyse_poussee:
    
    def __init__(self, df):
        self.df = df
        self.custom_stop_words = set()

    def app(self, sidebar=True):
        st.title('Page du wordcloud')  
        st.markdown("---")

        
        col1, col2 = st.columns([2, 1])
        self.df["Date de publication"] = pd.to_datetime(self.df["Date de publication"])
        if sidebar : self.sidebar_sliders()

        
        with col1:
            st.image(self.worcloud().to_array())
            # st.image(self.generate_wordcloud(df= self.df, column="Préconisations sanitaires").to_array())
        
        with col2:  
            Page_analyse_simples(self.df).visu_images() 
        st.metric(label="Nombre de produits observés", value=(self.df.shape[0]))
        st.markdown("---")
        # self.plot_duration_scatter()
        
    @decorator_log.log_execution_time
    def worcloud(self, column="Motif du rappel"):
        col1, col2 = st.columns(2)
        with col1:
            new_stop_words = st.text_input("Ajotuez un stop word (séparés par des ,):")
        with col2:
            new_discrim_words = st.text_input("Ajouter des mots pout filtrer la colonne (séparés par des ,):")
        if new_discrim_words:
            self.df = self.df[self.df[column].str.contains(new_discrim_words, case=False)]
        if new_stop_words:
            words_list = [word.strip().lower() for word in new_stop_words.split(',')]
            _ = self.custom_stop_words.update(words_list)

        wordcloud = self.generate_wordcloud(self.df, column)
        return wordcloud
    
    @decorator_log.log_execution_time
    def generate_wordcloud(self, df, column):
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')
        custom_stop_words = self.custom_stop_words
        stopwords_fr = set(stopwords.words('french'))

        _ = stopwords_fr.update(custom_stop_words)
        # tokenizer
        text = ' '.join(df[column].dropna())
       
        wordcloud = WordCloud(stopwords=stopwords_fr, width=1600, height=800).generate(text)

        return wordcloud    
    
    
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
    p = Page_analyse_poussee(get_cleaned_df())
    print(p.custom_stop_words)
    p.app()