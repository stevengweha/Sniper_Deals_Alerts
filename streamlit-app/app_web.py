import streamlit as st

# Configuration globale
st.set_page_config(
    page_title="Smart Buy Sentinel",
    page_icon="🎯",
    layout="wide"
)

st.title("🎯 Bienvenue sur Smart Buy Sentinel")

st.markdown("""
### Votre centre de contrôle Data
Utilisez le menu à gauche pour naviguer entre les différents modules :
*   **🛒 Shopping** : Analyse des prix eBay et Leboncoin.
*   **🚆 Transport** : Statistiques de ponctualité SNCF via dbt.
""")

st.info("Sélectionnez une page dans la barre latérale pour commencer.")

# Petit récapitulatif technique dans la sidebar
st.sidebar.success("Pipelines Airflow : OK ✅")
st.sidebar.info("Base de données : PostgreSQL")