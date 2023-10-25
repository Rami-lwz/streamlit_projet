import streamlit as st
import pandas as pd
from df_cleaner import get_cleaned_df
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import nltk
from nltk.corpus import stopwords
from pages.page_1__analyses_simples import Page_analyse_simples
import decorator_log
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import numpy as np

try: st.set_page_config(layout="wide") 
except: pass

class Page_wordcloud:
    
    def __init__(self, df):
        self.df = df
        self.custom_stop_words = set()
    @decorator_log.log_execution_time
    def app(self, sidebar=True):
        st.title('Page d\'IA')  
        st.markdown("---")
        col1, col2, col3 = st.columns([1,2,1])
        self.df["Date de publication"] = pd.to_datetime(self.df["Date de publication"])
        self.sidebar_sliders()
        num_clusters = 5
        cluster_distrib, cluster_terms_df = self.IA(num_clusters=num_clusters)
        with col1:
            st.dataframe(cluster_distrib)
        with col2:
            st.dataframe(cluster_terms_df)
        cols = st.columns(5)
        
        st.markdown('# Word clouds for each cluster\n')
        colormaps = ["Blues", "Greens", "Reds", "Purples", "Oranges"]
        for i in range(num_clusters):
            wordcloud = WordCloud(width=1000, height=800, background_color='black', colormap=colormaps[i]).generate(' '.join(cluster_terms_df[f'Cluster {i}']))
            
            with cols[i]:
                st.markdown(f'## Cluster {i}')
                st.image(wordcloud.to_array())
    @decorator_log.log_execution_time
    def IA(self, num_clusters):
        stop_words_french = [
            "alors", "au", "aucuns", "aussi", "autre", "avant", "avec", "avoir", "bon", "car", "ce", "cela", "ces", "ceux",
            "chaque", "ci", "comme", "comment", "dans", "un", "une", "dont", "de", "non", "des", "du", "dedans", "dehors", "depuis", "devrait", "doit", "donc",
            "dos", "début", "elle", "elles", "en", "encore", "essai", "est", "et", "eu", "fait", "faites", "fois", "font",
            "hors", "ici", "il", "ils", "je", "juste", "la", "le", "les", "leur", "là", "ma", "maintenant", "mais", "mes",
            "mine", "moins", "mon", "mot", "même", "ni", "nommés", "notre", "nous", "ou", "où", "par", "parce", "pas", "peut",
            "peu", "plupart", "pour", "pourquoi", "quand", "que", "quel", "quelle", "quelles", "quels", "qui", "sa", "sans",
            "ses", "seulement", "si", "sien", "son", "sont", "sous", "soyez", "sujet", "sur", "ta", "tandis", "tellement",
            "tels", "tes", "ton", "tous", "tout", "trop", "très", "tu", "voient", "vont", "votre", "vous", "vu", "ça", "étaient",
            "état", "étions", "été", "être"
        ]
        self.df['Motif du rappel'] = self.df['Motif du rappel'].fillna('')
        self.df['Risques encourus par le consommateur'] = self.df['Risques encourus par le consommateur'].fillna('')
        self.df['combined_text'] = self.df['Motif du rappel'] + " " + self.df['Risques encourus par le consommateur']
        vectorizer = TfidfVectorizer(max_features=1000,  # considering top 1000 features
                                    stop_words=stop_words_french,  # removing stop words
                                    use_idf=True)
        # Transformation des textes combinés en une matrice de fonctionnalités TF-IDF
        tfidf_matrix = vectorizer.fit_transform(self.df['combined_text'])
        # Effectuer un clustering K-means
        km = KMeans(n_clusters=num_clusters, init='k-means++', random_state=42)
        _ = km.fit(tfidf_matrix)
        # Obtenir les étiquettes de regroupement
        clusters = km.labels_.tolist()
        # Ajout d'une nouvelle colonne au self.dfframe d'origine avec les informations de cluster
        self.df['Cluster'] = clusters
        # Comptage du nombre de documents par cluster pour comprendre la distribution
        cluster_distribution = self.df['Cluster'].value_counts().sort_index()
        # Préparer un self.dfframe pour les meilleurs termes par cluster
        order_centroids = km.cluster_centers_.argsort()[:, ::-1]
        terms = vectorizer.get_feature_names_out()
        # Sauvegarder les 10 premiers mots pour chaque cluster
        cluster_terms = {}
        for i in range(num_clusters):
            top_terms = [terms[ind] for ind in order_centroids[i, :10]]
            cluster_terms[f"Cluster {i}"] = top_terms
        cluster_terms_df = pd.DataFrame(cluster_terms)
        return cluster_distribution, cluster_terms_df
    @decorator_log.log_execution_time
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