import streamlit as st
import pandas as pd
from df_cleaner import get_cleaned_df
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import nltk
from nltk.corpus import stopwords
from pages.page_1__analyses_simples import Page_analyse_simples
import decorator_log
import seaborn as sns
import altair as alt


try: st.set_page_config(layout="wide") 
except: pass

class Page_analyse_poussee:
    
    def __init__(self, df):
        self.df = df
        self.custom_stop_words = set()

    def app(self, sidebar=True):
        st.title('Page d\'analyses poussées')  
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
        self.plot_duration_scatter()
        st.markdown("---")
        self.hist_wordCloud()
        st.markdown("---")
        self.pie("Motif du rappel")


        
    @decorator_log.log_execution_time
    def worcloud(self, column="Motif du rappel"):
        st.write("Nuage de mot contenu dans le", column)
        col1, col2 = st.columns(2)
        with col1:
            new_stop_words = st.text_input("Ajoutez un stop word (séparés par des ,):")
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
    
    @decorator_log.log_execution_time
    def plot_duration_scatter(self):
        st.write("Durée entre commercialisation et rappel par categorie")
        self.df[['Début','Fin']] = self.df['Date début/Fin de commercialisation'].str.replace('Du ', '', regex=True).str.split(' au ', expand=True)
        self.df['Date début commercialisation'] = pd.to_datetime(self.df['Début'], dayfirst=True, errors='coerce')
        self.df['Date fin commercialisation'] = pd.to_datetime(self.df['Fin'], dayfirst=True, errors='coerce')

        # Calculate duration between the start and end of marketing
        self.df['Durée entre commercialisation et rappel'] = (self.df['Date fin commercialisation'] - self.df['Date début commercialisation']).dt.days

        # Remove rows where 'Durée entre commercialisation et rappel' is NaN
        self.df = self.df[self.df['Durée entre commercialisation et rappel'].notnull()]

        st.scatter_chart(self.df, x='Durée entre commercialisation et rappel', y='Catégorie de produit')

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

    @decorator_log.log_execution_time
    def hist_wordCloud(self, column="Motif du rappel"):
        st.write(f"Diagramme en barre des vingt mots les plus fréquents de la colonne {column}")

        # Obtenir les valeurs triées par ordre décroissant
        word_counts = self.df[column].value_counts().sort_values(ascending=False)

        # Sélectionner les 20 mots les plus fréquents (ou moins si moins de 20 mots uniques)
        top_words = word_counts.head(20)

        # Créer un graphique à barres en inversant les axes
        st.bar_chart(top_words)
        
    @decorator_log.log_execution_time
    def pie(self,column="Catégorie de produit"):
        df = self.df  # Assuming self.df is your DataFrame

        # First, prepare the data for the pie chart.
        # Group the data by category and count the records in each.
        categorie_counts = df[column].value_counts().reset_index()
        categorie_counts.columns = [column, 'Counts']

        # Calculate the percentage for each category
        total = categorie_counts['Counts'].sum()  # Sum of all counts (total number of records)
        categorie_counts['Percentage'] = (categorie_counts['Counts'] / total) * 100  # Calculate percentage

        # Create a pie chart
        pie_chart = alt.Chart(categorie_counts).mark_arc(
            innerRadius=50,  # 'Donut' shape
            outerRadius=250,
            stroke='white'
        ).encode(
            theta='Percentage:Q',  # Use the 'Percentage' field for pie segments
            color=alt.Color(f'{column}:N',legend=alt.Legend(title=f'{column}', orient='left', labelFontSize=18, titleFontSize=18, symbolSize=500, symbolType='circle')),
            tooltip=[alt.Tooltip(f'{column}:N'), alt.Tooltip('Percentage:Q', format='.2f', title='Percentage')]  # Show percentage on hover
        ).properties(
            title=f'Distribution des rappels par {column}  (%)',
            width=300,
            height=600
        ).configure_title(
            fontSize=20
        )

        # Display the chart in Streamlit
        st.altair_chart(pie_chart, use_container_width=True)

        # Display the chart in Streamlit
        st.altair_chart(pie_chart, use_container_width=True)

if __name__ == "__main__":
    p = Page_analyse_poussee(get_cleaned_df())
    print(p.custom_stop_words)
    p.app()