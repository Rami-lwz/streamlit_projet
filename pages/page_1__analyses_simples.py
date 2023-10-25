import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from df_cleaner import get_cleaned_df
import altair as alt
import random 
import decorator_log

try: st.set_page_config(layout="wide") 
except: pass

class Page_analyse_simples: 
    
    def __init__(self, df):
        self.df = df
    
    def app(self, sidebar=True):
        st.title('Page d\'analyses simples')          
        self.df["Date de publication"] = pd.to_datetime(self.df["Date de publication"])
        if sidebar : selected_categ, selected_brands = self.sidebar_sliders()
        st.markdown("---")
        st.metric(label="Nombre de produits observés", value=(self.df.shape[0]))
        st.markdown("---")
        self.visu_images()
        st.markdown("---")
        self.histo_recalls_per_month_or_day()
        st.markdown("---")
        if len(selected_brands) != 1:
            st.markdown("## Nombre de retours par Marque")
            self.retours_par_marque()
        else: st.markdown("## Distribution de la Nature Juridique du rappel pour " + selected_brands[0]); self.nature_juridique_marque_simple()
        st.markdown("---")
        if len(selected_categ) == 1:
            self.pie_categorie('Sous-catégorie de produit')
        else: self.pie_categorie('Catégorie de produit')
        st.markdown("---")
        if len(selected_categ) == 1:
            st.markdown("## Durée entre commercialisation et rappel pour " + selected_categ[0])
            self.plot_duration_scatter('Sous-catégorie de produit')
        else:
            st.markdown("## Durée entre commercialisation et rappel par Catégorie")
            self.plot_duration_scatter('Catégorie de produit')
        st.markdown("---")
        selected_columns = st.multiselect("Colonnes", self.df.columns)
        try : 
            self.df.drop(columns=["Unnamed: 0"], inplace=True)
        except: pass
        if selected_columns.__len__() > 0:
            df_show = self.df[selected_columns]
            st.dataframe(df_show)
        else :
            st.dataframe(self.df)
    @decorator_log.log_execution_time
    def bar_sousCategories(self,categorie):
        df = self.df.copy()
        df=df[df['Catégorie de produit']==categorie][['Sous-catégorie de produit']]
        group_by_sous_categorie=df.groupby('Sous-catégorie de produit').size()
        st.bar_chart(group_by_sous_categorie)
        
    @decorator_log.log_execution_time
    def histo_recalls_per_month_or_day(self):
        df = self.df
        # Generate a new column for month_year and day granularity
        df["month_year"] = df["Date de publication"].dt.to_period('M')  # This creates a PeriodIndex for months
        df["day"] = df["Date de publication"].dt.to_period('D')  # This creates a PeriodIndex for days

        # Determine if we need a monthly or daily plot
        unique_month_years = df["month_year"].nunique()
        st.write("## Nombre de retours par mois")
        if unique_month_years > 1:
            st.write("### À la maille Mensuelle")
            # Monthly plot logic remains the same
            count_df = df["month_year"].value_counts().rename_axis('month_year').reset_index(name='counts')
            count_df['month_year'] = count_df['month_year'].dt.strftime('%Y-%m')  # Convert Period to string
            count_df = count_df.sort_values(by="month_year")

            # Create the data for the chart
            chart_data = pd.DataFrame(count_df['counts'].values, index=count_df['month_year'], columns=['counts'])

            # Display the monthly chart
            st.line_chart(chart_data)
        else:
            st.write("### À la maille Journalière")
            # If only one month is selected, switch to daily granularity
            count_day_df = df["day"].value_counts().rename_axis('day').reset_index(name='counts')
            count_day_df['day'] = count_day_df['day'].dt.strftime('%Y-%m-%d')  # Convert Period to string
            count_day_df = count_day_df.sort_values(by="day")

            # Create the data for the chart
            chart_data_day = pd.DataFrame(count_day_df['counts'].values, index=count_day_df['day'], columns=['counts'])

            # Display the daily chart
            st.line_chart(chart_data_day)

    @decorator_log.log_execution_time
    def plot_duration_scatter(self, categorie):
        self.df[['Début','Fin']] = self.df['Date début/Fin de commercialisation'].str.replace('Du ', '', regex=True).str.split(' au ', expand=True)
        self.df['Date début commercialisation'] = pd.to_datetime(self.df['Début'], dayfirst=True, errors='coerce')
        self.df['Date fin commercialisation'] = pd.to_datetime(self.df['Fin'], dayfirst=True, errors='coerce')

        # Calculate duration between the start and end of marketing
        self.df['Durée entre commercialisation et rappel'] = (self.df['Date fin commercialisation'] - self.df['Date début commercialisation']).dt.days

        # Remove rows where 'Durée entre commercialisation et rappel' is NaN
        self.df = self.df[self.df['Durée entre commercialisation et rappel'].notnull()]

        st.scatter_chart(self.df, x='Durée entre commercialisation et rappel', y=categorie)

    @decorator_log.log_execution_time
    def retours_par_marque(self):
        df = self.df

        # Prepare the data
        product_brand_counts = df['Nom de la marque du produit'].value_counts().reset_index()
        product_brand_counts.columns = ['Brand', 'Counts']
        product_brand_counts = product_brand_counts.sort_values(by='Counts', ascending=False).head(10)

        # Create an Altair chart object
        chart = alt.Chart(product_brand_counts).mark_bar().encode(
            x=alt.X('Counts:Q', title='Nombre de retours'),
            y=alt.Y('Brand:N', sort='-x', title='Brand'),  # sorting by '-x' sorts based on the 'x' axis in descending order
            tooltip=['Brand', 'Counts']
        ).properties(
            title='',
            width=600,  # You can adjust dimensions as needed
            height=400
        ).configure_axis(
            labelFontSize=12,
            titleFontSize=14
        ).configure_title(
            fontSize=16
        )

        # Use Streamlit to render the plot
        st.altair_chart(chart, use_container_width=True)

    def nature_juridique_marque_simple(self):
        single_brand_df = self.df[self.df['Nom de la marque du produit'] == self.df['Nom de la marque du produit'].unique()[0]]

        # Let's assume 'Nature juridique du rappel' is a column in your dataframe
        nature_counts = single_brand_df['Nature juridique du rappel'].value_counts().reset_index()
        nature_counts.columns = ['Nature', 'Counts']

        # Create an Altair chart for 'Nature juridique du rappel'
        nature_chart = alt.Chart(nature_counts).mark_bar().encode(
            x=alt.X('Counts:Q', title='Nombre de retours'),
            y=alt.Y('Nature:N', sort='-x', title='Nature juridique du rappel'),
            tooltip=['Nature', 'Counts']
        ).properties(
            title="",
            width=600,
            height=400
        ).configure_axis(
            labelFontSize=12,
            titleFontSize=14
        ).configure_title(
            fontSize=16
        )
        st.altair_chart(nature_chart, use_container_width=True)
    
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

        # If specific categories are selected, filter the DataFrame
        if selected_categories:
            self.df = self.df[self.df['Catégorie de produit'].isin(selected_categories)]

        # Filter for 'Nom de la marque du produit'
        unique_brands = self.df['Nom de la marque du produit'].value_counts().index.unique()
        selected_brands = st.sidebar.multiselect('Select Nom de la marque du produit', options=unique_brands)

        # If specific brands are selected, filter the DataFrame
        if selected_brands:
            self.df = self.df[self.df['Nom de la marque du produit'].isin(selected_brands)]
        
        return selected_categories, selected_brands
    
    @decorator_log.log_execution_time
    def pie_categorie(self, categorie):
        df = self.df  # Assuming self.df is your DataFrame

        # First, prepare the data for the pie chart.
        # Group the data by category and count the records in each.
        categorie_counts = df[categorie].value_counts().reset_index()
        categorie_counts.columns = [categorie, 'Counts']

        # Calculate the percentage for each category
        total = categorie_counts['Counts'].sum()  # Sum of all counts (total number of records)
        categorie_counts['Percentage'] = (categorie_counts['Counts'] / total) * 100  # Calculate percentage

        # Create a pie chart
        pie_chart = alt.Chart(categorie_counts).mark_arc(
            innerRadius=50,  # 'Donut' shape
            outerRadius=100,
            stroke='white'
        ).encode(
            theta='Percentage:Q',  # Use the 'Percentage' field for pie segments
            color=alt.Color(categorie+':N', legend=alt.Legend(title="Catégories de produits")),
            tooltip=[alt.Tooltip(categorie+ ':N'), alt.Tooltip('Percentage:Q', format='.2f', title='Percentage')]  # Show percentage on hover
        ).properties(
            title='Distribution par '+ categorie + ' (%)',
            width=300,
            height=300
        ).configure_title(
            fontSize=20
        ).configure_legend(
            labelFontSize=12,
            titleFontSize=14
        )

        # Display the chart in Streamlit
        st.altair_chart(pie_chart, use_container_width=True)
        
    @decorator_log.log_execution_time
    def visu_images(self):
        valid_image_links_df = self.df[self.df["Liens vers les images"].notna()]

        if valid_image_links_df.empty:
            st.write("No images to display.")
            return

        # Ensure 'img_index' is in the session state and within bounds.
        if 'img_index' not in st.session_state or st.session_state['img_index'] >= len(valid_image_links_df):
            st.session_state['img_index'] = random.randint(0, len(valid_image_links_df) - 1)

        if st.button('Next'):
            # Also ensuring the new random index is within bounds after any potential DataFrame change.
            st.session_state['img_index'] = random.randint(0, len(valid_image_links_df) - 1)

        # Now that we've added checks above, we know 'img_index' is within bounds here.
        selected_row = valid_image_links_df.iloc[st.session_state['img_index']]

        col1, col2 = st.columns([1, 2])

        with col1:
            image_link = selected_row["Liens vers les images"].split(' ')[0]
            st.image(image_link, caption=selected_row["Noms des modèles ou références"], width=None, use_column_width="auto")

        with col2:
            st.write("**Additional Info:**")
            st.write("**Catégorie de produit:** " + str(selected_row["Catégorie de produit"]))
            st.write("**Nom de la marque du produit:** " + str(selected_row["Nom de la marque du produit"]))
            st.write("**Produit Réference:** " + str(selected_row["Noms des modèles ou références"]))
            st.write("**Zone géographique de vente:** " + str(selected_row["Zone géographique de vente"]))
            st.write("**Nature juridique du rappel:** " + str(selected_row["Nature juridique du rappel"]))
            st.write("**Motif du rappel:** " + str(selected_row["Motif du rappel"]))
            st.write(str(selected_row["Liens vers les images"]))

if __name__ == "__main__": 
    p = Page_analyse_simples(get_cleaned_df())
    p.app()