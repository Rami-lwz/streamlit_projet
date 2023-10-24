import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from df_cleaner import get_cleaned_df
import altair as alt

class Page_analyse_simples: 
    def __init__(self, df):
        self.df = df
    
    def app(self):
        st.title('Page d\'analyses simples')  
        
        self.df["Date de publication"] = pd.to_datetime(self.df["Date de publication"])
        
        self.sidebar_sliders()
        st.markdown("---")
        st.metric(label="Nombre de produits observés", value=(self.df.shape[0]))
        st.markdown("---")
        self.histo_recalls_per_month()
        self.retours_par_marque()
        self.pie_categorie()
        # show df
        
        selected_columns = st.multiselect("Colonnes", self.df.columns)
        # add the number of rows after filtering as a indicator
        # show df
        try : 
            self.df.drop(columns=["Unnamed: 0"], inplace=True)
        except: pass
        if selected_columns.__len__() > 0:
            df_show = self.df[selected_columns]
            st.dataframe(df_show)
        else :
            st.dataframe(self.df)
    
    def histo_recalls_per_month(self):
        df = self.df
        # Generate a new column to assist with plotting
        df["month_year"] = df["Date de publication"].dt.to_period('M')  # This creates a PeriodIndex

        # Count the number of recalls per 'month_year' and reset the index to use Streamlit charts properly
        count_df = df["month_year"].value_counts().rename_axis('month_year').reset_index(name='counts')
        count_df['month_year'] = count_df['month_year'].dt.strftime('%Y-%m')  # Convert Period to string for proper plotting
        count_df = count_df.sort_values(by="month_year") 

        # Create the data for the chart
        chart_data = pd.DataFrame(count_df['counts'].values, index=count_df['month_year'], columns=['counts'])

        # Display the chart
        st.bar_chart(chart_data)

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
            title='Nombre de retours par Marque',
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

    def pie_categorie(self):
        df = self.df  # Assuming self.df is your DataFrame

        # First, we'll need to prepare the data for the pie chart.
        # This involves grouping the data by category and counting the records in each.
        categorie_counts = df['Catégorie de produit'].value_counts().reset_index()
        categorie_counts.columns = ['Catégorie de produit', 'Counts']
        categorie_counts = categorie_counts.sort_values('Counts', ascending=False)

        # Create a pie chart
        pie_chart = alt.Chart(categorie_counts).mark_arc(
            innerRadius=50,  # This makes the pie chart to have a 'donut' shape
            outerRadius=100,
            stroke='white'  # This creates a white line between segments
        ).encode(
            theta='Counts:Q',  # This tells Altair which field to use to create pie segments
            color=alt.Color('Catégorie de produit:N', legend=alt.Legend(title="Catégories de produits")),  # This tells which field should define the color
            tooltip=['Catégorie de produit', 'Counts']  # Shows data on hover
        ).properties(
            title='Distribution by Category',
            width=300,  # you can adjust dimensions as needed
            height=300
        ).configure_title(
            fontSize=20
        ).configure_legend(
            labelFontSize=12,
            titleFontSize=14
        )

        # Display the chart in Streamlit
        st.altair_chart(pie_chart, use_container_width=True)

if __name__ == "__main__": 
    p = Page_analyse_simples(get_cleaned_df())
    p.app()