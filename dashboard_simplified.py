"""
Dashboard Streamlit Simplifié - Smart Buy Sentinel
Adapté à la structure MongoDB réelle
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# ============================================
# CONFIG PAGE
# ============================================
st.set_page_config(
    page_title="Smart Buy Sentinel",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CONNEXION MONGODB
# ============================================
@st.cache_resource
def get_mongo_client():
    """Connexion MongoDB avec cache"""
    mongo_uri = os.getenv("MONGODB_URI")
    if not mongo_uri:
        st.error("❌ MONGODB_URI non configurée")
        st.stop()
    return MongoClient(mongo_uri)

@st.cache_data(ttl=300)  # Cache 5 minutes
def load_deals():
    """Charge les deals de MongoDB"""
    try:
        client = get_mongo_client()
        db = client["smart_buy"]
        collection = db["deals"]
        
        deals = list(collection.find())
        if not deals:
            st.warning("⚠️ Aucun deal trouvé dans la base")
            return pd.DataFrame()
        
        df = pd.DataFrame(deals)
        # Convertir _id en string si nécessaire
        if "_id" in df.columns:
            df["_id"] = df["_id"].astype(str)
        
        return df
    except Exception as e:
        st.error(f"❌ Erreur de connexion MongoDB: {e}")
        return pd.DataFrame()

# ============================================
# CHARGEMENT DONNÉES
# ============================================
df_raw = load_deals()

if df_raw.empty:
    st.stop()

# ============================================
# BARRE LATÉRALE - FILTRES SIMPLIFIÉS
# ============================================
with st.sidebar:
    st.markdown("# 🎯 Filtres")
    st.markdown("---")
    
    # Filtre Catégorie
    categories = ['📍 Toutes les catégories'] + sorted(
        df_raw['category'].dropna().unique().tolist()
    )
    selected_category = st.selectbox(
        "📂 Catégorie",
        categories,
        key="category_filter"
    )
    df_step1 = df_raw if selected_category == '📍 Toutes les catégories' \
        else df_raw[df_raw['category'] == selected_category]
    
    # Filtre Marque
    brands = ['🏷️ Toutes les marques'] + sorted(
        df_step1['brand'].dropna().unique().tolist()
    )
    selected_brand = st.selectbox(
        "🏷️ Marque",
        brands,
        key="brand_filter"
    )
    df_step2 = df_step1 if selected_brand == '🏷️ Toutes les marques' \
        else df_step1[df_step1['brand'] == selected_brand]
    
    # Filtre Modèle
    models = ['📱 Tous les modèles'] + sorted(
        df_step2['product_model'].dropna().unique().tolist()
    )
    selected_model = st.selectbox(
        "📱 Modèle",
        models,
        key="model_filter"
    )
    df_step3 = df_step2 if selected_model == '📱 Tous les modèles' \
        else df_step2[df_step2['product_model'] == selected_model]
    
    st.markdown("---")
    
    # Filtre Prix (slider dynamique)
    if not df_step3.empty:
        min_price = float(df_step3['price'].min())
        max_price = float(df_step3['price'].max())
        
        if min_price == max_price:
            max_price += 100
        
        price_range = st.slider(
            "💰 Plage de Prix (€)",
            min_price, max_price,
            (min_price, max_price),
            key="price_range"
        )
    else:
        price_range = (0.0, 10000.0)
    
    # Filtre Profit minimum
    st.markdown("**Profit Minimum**")
    min_profit = st.number_input("€", value=0, min_value=0, step=50, key="min_profit")
    
    st.markdown("---")
    
    # Recherche libre
    search_query = st.text_input(
        "🔍 Recherche",
        placeholder="Ex: MacBook, iPhone...",
        key="search"
    )

# ============================================
# APPLICATION DES FILTRES
# ============================================
df_filtered = df_step3.copy()

# Filtre prix
if 'price' in df_filtered.columns:
    df_filtered = df_filtered[
        (df_filtered['price'] >= price_range[0]) & 
        (df_filtered['price'] <= price_range[1])
    ]

# Filtre profit
if 'estimated_resell_profit' in df_filtered.columns:
    df_filtered = df_filtered[df_filtered['estimated_resell_profit'] >= min_profit]

# Recherche texte
if search_query and 'title' in df_filtered.columns:
    keywords = search_query.lower().split()
    mask = df_filtered['title'].fillna('').str.lower().apply(
        lambda x: all(k in str(x) for k in keywords)
    )
    df_filtered = df_filtered[mask]

# ============================================
# HEADER PRINCIPAL
# ============================================
st.markdown("# 💎 Smart Buy Sentinel")
st.markdown(f"**{len(df_filtered)}** offres disponibles | Actualisé : {datetime.now().strftime('%H:%M')}")

# KPIs
col1, col2, col3, col4 = st.columns(4)

with col1:
    avg_price = df_filtered['price'].mean() if not df_filtered.empty else 0
    st.metric(
        "💰 Prix Moyen",
        f"{avg_price:.0f} €" if avg_price > 0 else "N/A",
        delta=None
    )

with col2:
    min_price_val = df_filtered['price'].min() if not df_filtered.empty else 0
    st.metric(
        "🔥 Meilleur Prix",
        f"{min_price_val:.0f} €" if min_price_val > 0 else "N/A"
    )

with col3:
    avg_profit = df_filtered['estimated_resell_profit'].mean() \
        if not df_filtered.empty and 'estimated_resell_profit' in df_filtered.columns else 0
    st.metric(
        "📈 Gain Moyen",
        f"+{avg_profit:.0f} €" if avg_profit > 0 else "N/A",
        delta="+5%" if avg_profit > 0 else None
    )

with col4:
    active_count = len(df_filtered[df_filtered['operational_status'].fillna('').str.contains('🟢', na=False)]) \
        if 'operational_status' in df_filtered.columns else 0
    st.metric(
        "🟢 Actifs",
        active_count
    )

st.markdown("---")

# ============================================
# AFFICHAGE PRINCIPAL
# ============================================
st.markdown("## ⚡ Meilleures Opportunités")

if not df_filtered.empty:
    # Trier par profit
    df_display = df_filtered.sort_values(
        'estimated_resell_profit',
        ascending=False
    )
    
    # Affichage en cartes
    num_cols = 3
    cols = st.columns(num_cols)
    
    for idx, (_, deal) in enumerate(df_display.iterrows()):
        col_idx = idx % num_cols
        
        with cols[col_idx]:
            with st.container(border=True):
                # En-tête
                col_source, col_status = st.columns([2, 1])
                with col_source:
                    source = str(deal.get('source', 'Unknown')).upper()
                    st.markdown(f"**{source}**")
                
                with col_status:
                    status = "🟢" if deal.get('operational_status') == '🟢 Actif' else "⚪"
                    st.markdown(status, help="Statut")
                
                # Titre
                title = str(deal.get('title', ''))[:50]
                st.markdown(f"**{title}**")
                
                # Détails principaux
                st.markdown(f"""
                **Modèle:** {deal.get('product_model', 'N/A')}  
                **État:** {deal.get('product_condition', 'N/A')}  
                **Marque:** {deal.get('brand', 'N/A')}
                """)
                
                # Prix et Profit
                price = deal.get('price', 0)
                profit = deal.get('estimated_resell_profit', 0)
                deal_score = deal.get('deal_score', '📊 Standard')
                
                st.markdown(f"### {price:.0f} €")
                
                if profit > 0:
                    profit_color = "🟢"
                    st.markdown(
                        f"{profit_color} **Gain estimé: +{profit:.0f} €**"
                    )
                else:
                    st.markdown(f"⚪ Aucun gain détecté")
                
                # Score deal
                st.caption(f"{deal_score}")
                
                # Lien vers l'offre
                url = deal.get('url')
                if url and pd.notna(url):
                    st.link_button(
                        "🔗 Voir l'offre",
                        str(url),
                        use_container_width=True
                    )
else:
    st.info("💡 Aucune offre ne correspond à vos critères.")

# ============================================
# ONGLET DONNÉES COMPLÈTES
# ============================================
st.markdown("---")
st.markdown("## 📊 Vue Complète des Données")

if not df_filtered.empty:
    # Sélection colonnes à afficher
    display_columns = [
        'source', 'brand', 'product_model', 'price',
        'estimated_resell_profit', 'deal_score', 'operational_status'
    ]
    
    available_cols = [col for col in display_columns if col in df_filtered.columns]
    df_display_table = df_filtered[available_cols].copy()
    
    # Formattage
    df_display_table = df_display_table.rename(columns={
        'source': '🛒 Source',
        'brand': '🏷️ Marque',
        'product_model': '📱 Modèle',
        'price': '💰 Prix (€)',
        'estimated_resell_profit': '📈 Gain (€)',
        'deal_score': '💎 Score',
        'operational_status': '🟢 Statut'
    })
    
    st.dataframe(
        df_display_table,
        use_container_width=True,
        height=400
    )
    
    # Téléchargement CSV
    csv = df_display_table.to_csv(index=False)
    st.download_button(
        label="📥 Télécharger (CSV)",
        data=csv,
        file_name=f"deals_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv",
        use_container_width=True
    )

# ============================================
# STATS SIMPLES
# ============================================
st.markdown("---")
st.markdown("## 📈 Statistiques")

col1, col2, col3 = st.columns(3)

with col1:
    if not df_filtered.empty and 'price' in df_filtered.columns:
        st.metric(
            "Prix Médian",
            f"{df_filtered['price'].median():.0f} €"
        )

with col2:
    if not df_filtered.empty and 'estimated_resell_profit' in df_filtered.columns:
        profitable = len(df_filtered[df_filtered['estimated_resell_profit'] > 0])
        st.metric(
            "Offres Rentables",
            f"{profitable}/{len(df_filtered)}"
        )

with col3:
    if not df_filtered.empty and 'source' in df_filtered.columns:
        best_source = df_filtered['source'].value_counts().idxmax()
        st.metric(
            "Meilleure Plateforme",
            best_source.upper()
        )
