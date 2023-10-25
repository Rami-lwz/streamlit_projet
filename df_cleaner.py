
import pandas as pd
import os
def fillna(df, col, value):
    # fillna sur une colonne
    df[col] = df[col].fillna(value)
    return df

def fillnas(df, dictio):
    # plusieurs fillna en même temps
    for k, v in dictio.items():
        df = fillna(df, k, v)
    return df

def replace_value_in_col(df, col:str, dictio:dict):
    # remplace les valeurs d'une colonne par d'autres
    df[col] = df[col].replace(dictio)
    return df

def replace_values_in_cols(df, dictio:dict):
    # remplace les valeurs de plusieurs colonnes par d'autres
    for col, values in dictio.items():
        df = replace_value_in_col(df, col, values)
    return df

def clean_distributeurs(df):
    df["Distributeurs"] = df["Distributeurs"].apply(lambda x: x.lower() if type(x) == str else x)
    df["Distributeurs"] = df["Distributeurs"].apply(lambda x: x.replace("\r\n", ",") if type(x) == str else x)

    a = df['Distributeurs'].dropna().unique().tolist()
    b = a
    # b = liste des distributeurs dont le nom est plus long que 10 caractères
    list_distrib = [i.lower() for i in ["AUCHAN", "CARREFOUR", "SYSTEME U", 
                    "CASINO", "INTERMARCHE", "LEADER PRICE", 
                    "LECLERC", "ATAC", "CANTREL SALAISON SARL",
                    "CORA", "LKB INTERNATIONAL", "LIDL", "MONOPRIX", 
                    "AMAZON", "CDISCOUNT", "FRANPRIX", "LEADER PRICE", "FNAC",
                    "DARTY", "HYPERMARCHé", "MONOPRIX", " U ", "LA RUCHE QUI DIT OUI"]]
    # not any but more than one
    c = [i for i in b if sum([j.lower() in i.lower() for j in list_distrib]) > 1]
    # c = liste des distributeurs dont le nom contient plus d'un nom de grands distributeurs
    d = [i for i in b if sum([j.lower() in i.lower() for j in list_distrib]) == 1]
    # d = liste des distributeurs dont le nom contient un seul nom de grands distributeurs
    df.loc[df["Distributeurs"].isin([i for i in c]), "Distributeurs"] = "Plusieurs Grands Distributeurs"
    
    for i in d:
        for j in list_distrib:
            if j.lower() in i.lower():
                if j == " U ":
                    df.loc[df["Distributeurs"] == i, "Distributeurs"] = "SYSTEME U"
                else:
                    # print("replace", i, "by", j)
                    df.loc[df["Distributeurs"] == i, "Distributeurs"] = j
    df.loc[df["Distributeurs"] == "/", "Distributeurs"] = "Non Renseigné"

    return df

def clean_nom_marque(df):
    df["Nom de la marque du produit"] = df["Nom de la marque du produit"].apply(lambda x: x.lower() if type(x) == str else x)
    df["Nom de la marque du produit"] = df["Nom de la marque du produit"].apply(lambda x: x.replace("\r\n", ",") if type(x) == str else x)

    a = df['Nom de la marque du produit'].dropna().unique().tolist()
    b = a
    # b = liste des Nom de la marque du produit dont le nom est plus long que 10 caractères
    list_distrib = [i.lower() for i in ["AUCHAN", "CARREFOUR", "SYSTEME U", 
                    "CASINO", "INTERMARCHE", "LEADER PRICE", 
                    "LECLERC", "ATAC", "CANTREL SALAISON SARL",
                    "CORA", "LKB INTERNATIONAL", "LIDL", "MONOPRIX", 
                    "AMAZON", "CDISCOUNT", "FRANPRIX", "LEADER PRICE", "FNAC",
                    "DARTY", "HYPERMARCHé", "MONOPRIX", " U ", "LA RUCHE QUI DIT OUI"]]
    # not any but more than one
    c = [i for i in b if sum([j.lower() in i.lower() for j in list_distrib]) > 1]
    # c = liste des Nom de la marque du produit dont le nom contient plus d'un nom de grands Nom de la marque du produit
    d = [i for i in b if sum([j.lower() in i.lower() for j in list_distrib]) == 1]
    # d = liste des Nom de la marque du produit dont le nom contient un seul nom de grands Nom de la marque du produit
    df.loc[df["Nom de la marque du produit"].isin([i for i in c]), "Nom de la marque du produit"] = "Marque de Grand Distributeur"
    
    
    # Remplacer les "Carrefour BIO", "CARREFOUR LIMOSGES" etc. par juste "carrefour" et ceci pour tous les grands distributeurs de notre liste
    for i in d:
        for j in list_distrib:
            if j.lower() in i.lower():
                if j == " U ":
                    df.loc[df["Nom de la marque du produit"] == i, "Nom de la marque du produit"] = "SYSTEME U"
                else:
                    # print("replace", i, "by", j)
                    df.loc[df["Nom de la marque du produit"] == i, "Nom de la marque du produit"] = j.lower()
    df.loc[df["Nom de la marque du produit"] == "/", "Nom de la marque du produit"] = "sans marque"
    df.loc[df["Nom de la marque du produit"] == "sans marque", "Nom de la marque du produit"] = df["Distributeurs"]
    return df

def get_cleaned_df():
    try: 
        df = pd.read_csv(os.path.join(os.getcwd() + ("/data/cleaned_df.csv")), sep=";")
    except:
        df = pd.read_csv(
            os.path.join(os.getcwd() + ("/data/rappelconso0.csv")), sep=";"
        ).rename(
                {"﻿Référence Fiche": "Référence Fiche"}, axis=1
        )
        df = fillnas(df, {"Nature juridique du rappel": "Volontaire (sans arrêté préfectoral)",
                    "Catégorie de produit": "Non Catégorié",
                    "Sous-catégorie de produit": "Non Catégorisé",
                    'Distributeurs':'Non Spécifié',
                    'Modalités de compensation' : "Non Spécifié",
                    'Date de fin de la procédure de rappel' : "Non Spécifié"
        })
        df = clean_nom_marque(clean_distributeurs(df))
        df["Nom de la marque du produit"] = df["Nom de la marque du produit"].apply(lambda x: x.capitalize() if type(x) == str else x)
        df["Distributeurs"] = df["Distributeurs"].apply(lambda x: x.capitalize() if type(x) == str else x)
        df.to_csv(os.path.join(os.getcwd() + ("/data/cleaned_df.csv")), sep=";")
    
    return df