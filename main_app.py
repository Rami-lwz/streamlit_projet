# main_app.py
import streamlit as st
import pandas as pd
import os
from df_cleaner import get_cleaned_df
columns = [
 'Référence Fiche',
 'N° de Version',
 'Nature juridique du rappel',
 'Catégorie de produit',
 'Sous-catégorie de produit',
 'Nom de la marque du produit',
 'Noms des modèles ou références',
 'Identification des produits',
 'Conditionnements',
 'Date début/Fin de commercialisation',
 'Température de conservation',
 'Marque de salubrité',
 'Informations complémentaires',
 'Zone géographique de vente',
 'Distributeurs',
 'Motif du rappel',
 'Risques encourus par le consommateur',
 'Préconisations sanitaires',
 'Description complémentaire du risque',
 'Conduites à tenir par le consommateur',
 'Numéro de contact',
 'Modalités de compensation',
 'Date de fin de la procédure de rappel',
 'Informations complémentaires publiques',
 'Liens vers les images',
 'Lien vers la liste des produits',
 'Lien vers la liste des distributeurs',
 'Lien vers affichette PDF',
 'Lien vers la fiche rappel',
 'RappelGuid',
 'Date de publication'
]

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