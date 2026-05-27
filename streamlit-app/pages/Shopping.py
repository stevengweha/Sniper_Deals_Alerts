import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine
from dotenv import load_dotenv

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Smart Buy Sentinel | Scanner de Marché", 
    page_icon="🎯", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- STYLE CSS PERSONNALISÉ (INTERFACE & SIDEBAR) ---
st.markdown("""
    <style>
    /* Global et conteneurs */
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    
    /* Cartes des KPIs (Metrics) */
    div[data-testid="stMetric"] {
        background-color: #f8f9fa !important;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #e9ecef;
    }
    div[data-testid="stMetric"] * {
        color: #1f1f1f !important;
    }
    .stTooltipContent { background-color: white !important; color: black !important; }
    
    /* ---- REFONTE DE LA BARRE LATÉRALE ---- */
    section[data-testid="stSidebar"] {
        background-color: #0e1117 !important; /* Fond sombre pro */
        border-right: 1px solid #1e293b;
    }
    
    /* Titre principal Sidebar */
    section[data-testid="stSidebar"] h1 {
        color: #f8fafc !important;
        font-size: 20px !important;
        font-weight: 700 !important;
        margin-top: -10px !important;
    }
    
    /* Labels des filtres */
    section[data-testid="stSidebar"] label p {
        color: #cbd5e1 !important;
        font-weight: 500 !important;
        font-size: 13px !important;
        letter-spacing: 0.5px;
    }
    
    /* Conteneurs de champs (Selectbox, Text input, Multiselect) */
    section[data-testid="stSidebar"] div[data-baseweb="select"], 
    section[data-testid="stSidebar"] div[data-baseweb="input"] {
        background-color: #1e293b !important;
        border-radius: 8px !important;
        border: 1px solid #334155 !important;
    }
    
    /* Input texte focus & couleur */
    section[data-testid="stSidebar"] input {
        color: #f8fafc !important;
    }
    
    /* Séparateur horizontal */
    section[data-testid="stSidebar"] hr {
        margin: 15px 0 !important;
        border-color: #334155 !important;
    }
    </style>
""", unsafe_allow_html=True)

# Charger les variables d'environnement
load_dotenv()
DB_URL = os.getenv("DB_URL")

@st.cache_resource
def get_engine():
    """Initialisation unique du moteur SQLAlchemy"""
    return create_engine(DB_URL)

@st.cache_data(ttl=60, show_spinner=False)
def fetch_data():
    """Récupération des données depuis la table final_data"""
    try:
        engine = get_engine()
        query = "SELECT * FROM public_shopping.final_data ORDER BY estimated_resell_profit DESC"
        df = pd.read_sql(query, engine)
        
        # Cast des types et gestion des valeurs manquantes
        numeric_cols = ['price', 'pct_deviation', 'estimated_resell_profit', 
                        'z_score', 'model_volume', 'median_model_price', 
                        'avg_model_price', 'model_price_volatility', 'category_volume', 'data_age_hours']
        
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Conversion des dates
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        
        # Remplissage par défaut intelligent conforme au modèle dbt simplifié
        df['model_volume'] = df['model_volume'].fillna(1)
        df['median_model_price'] = df['median_model_price'].fillna(df['price'])
        df['estimated_resell_profit'] = df['estimated_resell_profit'].fillna(0)
        df['z_score'] = df['z_score'].fillna(0)
        df['data_age_hours'] = df['data_age_hours'].fillna(24)
        df['storage_capacity'] = df['storage_capacity'].fillna('Non spécifié')
        df['brand'] = df['brand'].fillna('Inconnue')
        df['product_model'] = df['product_model'].fillna('Modèle non répertorié')
        
        return df.dropna(subset=['price', 'timestamp'])
    
    except Exception as e:
        st.error(f"❌ Erreur de connexion à la base de données : {e}")
        return pd.DataFrame()

# Chargement des données
df_raw = fetch_data()

if df_raw.empty:
    st.error("❌ Aucune donnée disponible. Vérifiez la structure de la table ou votre connexion.")
    st.stop()

# --- BARRE LATÉRALE DE RECHERCHE ET FILTRAGE ---
with st.sidebar:
    st.markdown("<div style='text-align: center; padding-bottom: 10px;'><img src='https://cdn-icons-png.flaticon.com/512/833/833314.png' width='60'></div>", unsafe_allow_html=True)
    st.title("🎯 Options du Radar")
    st.markdown("---")
    
    # 1. Filtre Catégorie
    categories = ['Toutes'] + sorted(df_raw['category'].dropna().unique().tolist())
    selected_category = st.selectbox("📂 Catégorie", categories, key="category_filter")
    df_step1 = df_raw if selected_category == 'Toutes' else df_raw[df_raw['category'] == selected_category]

    # 2. Filtre Marque
    brands = ['Toutes'] + sorted(df_step1['brand'].dropna().unique().tolist())
    selected_brand = st.selectbox("🏷️ Marque", brands, key="brand_filter")
    df_step2 = df_step1 if selected_brand == 'Toutes' else df_step1[df_step1['brand'] == selected_brand]

    # 3. Filtre Modèle
    models = ['Tous'] + sorted(df_step2['product_model'].dropna().unique().tolist())
    selected_model = st.selectbox("📱 Modèle Spécifique", models, key="model_filter")
    df_step3 = df_step2 if selected_model == 'Tous' else df_step2[df_step2['product_model'] == selected_model]

    # 4. Filtre Capacité
    capacities = ['Toutes'] + sorted(df_step3['storage_capacity'].dropna().unique().tolist())
    selected_capacity = st.selectbox("💾 Capacité de Stockage", capacities, key="capacity_filter")
    df_step4 = df_step3 if selected_capacity == 'Toutes' else df_step3[df_step3['storage_capacity'] == selected_capacity]

    # 5. Filtres transversaux
    search_query = st.text_input("🔍 Recherche par mot-clé", placeholder="Ex: Pro Max, 5G...", key="search")
    
    available_sources = df_step4['source'].dropna().unique().tolist() if 'source' in df_step4.columns else []
    source_filter = st.multiselect("🛒 Plateformes", available_sources, default=available_sources, key="source_filter")
    
    available_conditions = df_step4['product_condition'].dropna().unique().tolist() if 'product_condition' in df_step4.columns else []
    condition_filter = st.multiselect("🛡️ État du produit", available_conditions, default=available_conditions, key="condition_filter")

    # 6. Slider Budget Dynamique & Sécurisé
    if not df_step4.empty:
        max_price = float(df_step4['price'].max())
        min_price = float(df_step4['price'].min())
        
        # Sécurité anti-crash si le dataset filtré ne contient qu'une seule valeur de prix
        if min_price == max_price:
            max_price += 1.0
            
        price_range = st.slider("💰 Plage de Prix (€)", min_price, max_price, (min_price, max_price), key="price_range")
    else:
        price_range = (0.0, 1000.0)

# Application des masques booléens de filtrage
try:
    final_mask = pd.Series([True] * len(df_step4), index=df_step4.index)
    
    if source_filter and 'source' in df_step4.columns:
        final_mask &= df_step4['source'].isin(source_filter)
    
    if condition_filter and 'product_condition' in df_step4.columns:
        final_mask &= df_step4['product_condition'].isin(condition_filter)
    
    if 'price' in df_step4.columns:
        final_mask &= df_step4['price'].between(price_range[0], price_range[1])
    
    if search_query and 'title' in df_step4.columns:
        keywords = search_query.lower().split()
        final_mask &= df_step4['title'].fillna('').str.lower().apply(lambda x: all(k in str(x) for k in keywords))
    
    df_filtered = df_step4[final_mask].copy()
    
except Exception as e:
    st.error(f"❌ Erreur lors du filtrage dynamique : {e}")
    df_filtered = df_step4.copy()

# --- HEADER ET KPIs ---
st.markdown("# 📡 Intelligence de Marché Sentinel")
st.caption(f"Analyse comparative basée sur le modèle global d'appareil — **{len(df_filtered)}** offres filtrées.")

col1, col2, col3, col4 = st.columns(4)

with col1:
    avg_price = df_filtered['price'].mean() if not df_filtered.empty else 0
    st.metric("Prix Moyen Constaté", f"{avg_price:.2f} €" if avg_price > 0 else "N/A")

with col2:
    min_price_val = df_filtered['price'].min() if not df_filtered.empty else 0
    st.metric("Meilleure Option d'Achat", f"{min_price_val:.2f} €" if min_price_val > 0 else "N/A")

with col3:
    if not df_filtered.empty and 'estimated_resell_profit' in df_filtered.columns:
        profit_data = df_filtered[df_filtered['estimated_resell_profit'] > 0]
        if not profit_data.empty and 'source' in profit_data.columns:
            best_source = profit_data.groupby('source')['estimated_resell_profit'].mean().idxmax()
            st.metric("Canal d'Achat Rentable", str(best_source).upper())
        else:
            st.metric("Canal d'Achat Rentable", "N/A")
    else:
        st.metric("Canal d'Achat Rentable", "N/A")

with col4:
    alerts_count = len(df_filtered[df_filtered['operational_status'].fillna('').str.contains('SNIPER')]) if 'operational_status' in df_filtered.columns else 0
    st.metric("🚨 Signaux Sniper Actifs", alerts_count)

st.markdown("<br>", unsafe_allow_html=True)

# --- NAVIGATION PAR ONGLETS ---
tab1, tab2, tab3, tab4 = st.tabs([
    "💎 Scanner d'Opportunités", 
    "🗺️ Analyse des Volumes & Marges", 
    "📉 Volatilité & Distributions", 
    "📋 Registre de Données Mart"
])

# ==========================================
# ONGLET 1 : SNIPER RADAR
# ==========================================
with tab1:
    if not df_filtered.empty and 'estimated_resell_profit' in df_filtered.columns:
        profitable_deals = df_filtered[df_filtered['estimated_resell_profit'] > 0]
        
        if not profitable_deals.empty:
            best_deal = profitable_deals.loc[profitable_deals['estimated_resell_profit'].idxmax()]
            
            st.markdown("### ⚡ Opportunité Or à Saisir Immédiatement")
            c_gauge, c_info = st.columns([1.2, 2])
            
            with c_gauge:
                max_profit = float(max(200, best_deal['estimated_resell_profit'] * 1.3))
                fig_gauge = go.Figure(go.Indicator(
                    mode="gauge+number+delta",
                    value=float(best_deal['estimated_resell_profit']),
                    number={'prefix': "+", 'suffix': " €", 'font': {'size': 36}},
                    delta={'reference': 0, 'increasing': {'color': "green"}},
                    title={'text': "Plus-value vs Médiane Modèle", 'font': {'size': 14}},
                    gauge={
                        'axis': {'range': [0, max_profit]},
                        'bar': {'color': "#00cc96"},
                        'steps': [
                            {'range': [0, 40], 'color': "#f8d7da"},
                            {'range': [40, 100], 'color': "#fff3cd"},
                            {'range': [100, max_profit], 'color': "#d1e7dd"}
                        ]
                    }
                ))
                fig_gauge.update_layout(height=230, margin=dict(l=20, r=20, t=30, b=25))
                st.plotly_chart(fig_gauge, use_container_width=True)

            with c_info:
                deal_score = best_deal.get('deal_score', '📊 PRIX DU MARCHÉ')
                status_color = "🔴" if "SURÉVALUÉ" in str(deal_score) else "🟢"
                st.markdown(f"### {status_color} {deal_score}")
                st.markdown(f"**{str(best_deal.get('title', ''))[:110]}...**")
                
                det1, det2 = st.columns(2)
                with det1:
                    st.markdown(f"🔹 **Prix Demandé :** `{best_deal['price']:.2f} €`")
                    st.markdown(f"🔹 **Médiane Référence Modèle :** `{best_deal['median_model_price']:.2f} €`")
                with det2:
                    st.markdown(f"🔹 **Modèle :** `{best_deal['product_model']}`")
                    st.markdown(f"🔹 **Capacité Spécifiée :** `{best_deal['storage_capacity']}`")
                    st.markdown(f"🔹 **Ancienneté :** `{best_deal['data_age_hours']} h`")
                
                if 'url' in best_deal and pd.notna(best_deal['url']):
                    st.link_button("🚀 OUVRIR L'OFFRE EN DIRECT", str(best_deal['url']), type="primary", use_container_width=True)
        else:
            st.info("💡 Aucun écart de prix positif détecté sur la sélection actuelle.")
    
    st.markdown("---")
    st.markdown("### 💎 Top 10 des Meilleures Marges (Calculées à l'échelle du Modèle)")

    if not df_filtered.empty and 'estimated_resell_profit' in df_filtered.columns:
        top_deals = df_filtered.sort_values('estimated_resell_profit', ascending=False).head(10)
        if not top_deals.empty:
            cols = st.columns(min(5, len(top_deals)))
            for idx, (_, row) in enumerate(top_deals.iterrows()):
                col_idx = idx % len(cols)
                with cols[col_idx]:
                    with st.container(border=True):
                        st.markdown(f"**{str(row['source']).upper()}**")
                        st.caption(f"📱 {str(row['product_model'])[:25]}")
                        st.caption(f"💾 {str(row['storage_capacity'])}")
                        
                        short_title = str(row['title'])[:35] + "..." if len(str(row['title'])) > 35 else str(row['title'])
                        st.markdown(f"<p style='font-size:12px; height:40px; margin-bottom:2px;'>{short_title}</p>", unsafe_allow_html=True)
                        st.markdown(f"### {row['price']:.0f} €")
                        
                        p_color = "green" if row['estimated_resell_profit'] > 0 else "grey"
                        st.markdown(f"<span style='color:{p_color}; font-weight:bold; font-size:13px;'>Gain: +{row['estimated_resell_profit']:.0f} €</span>", unsafe_allow_html=True)
                        
                        if 'url' in row and pd.notna(row['url']):
                            st.link_button("Voir l'offre", str(row['url']), use_container_width=True)

# ==========================================
# ONGLET 2 : VOLUMES & MAPS
# ==========================================
with tab2:
    if not df_filtered.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🗺️ Cartographie des Modèles Globaux")
            st.caption("Taille de case = Volume de marché du modèle. Couleur = Profitabilité moyenne.")
            
            if all(col in df_filtered.columns for col in ['category', 'brand', 'product_model', 'estimated_resell_profit']):
                fig_tree = px.treemap(
                    df_filtered, 
                    path=['category', 'brand', 'product_model'], 
                    values='model_volume',
                    color='estimated_resell_profit',
                    color_continuous_scale='RdYlGn',
                    color_continuous_midpoint=0,
                    hover_data=['price', 'estimated_resell_profit']
                )
                fig_tree.update_layout(height=400, margin=dict(t=10, b=0, l=0, r=0))
                fig_tree.update_traces(textinfo="label+value")
                st.plotly_chart(fig_tree, use_container_width=True)
        
        with col2:
            st.markdown("#### 🎯 Matrice d'Arbitrage : Prix Direct vs Plus-value")
            st.caption("Le volume bulle représente la masse globale d'annonces du modèle.")
            
            if all(col in df_filtered.columns for col in ['price', 'estimated_resell_profit']):
                fig_scatter = px.scatter(
                    df_filtered.head(700),
                    x="price", 
                    y="estimated_resell_profit", 
                    color="source" if 'source' in df_filtered.columns else None,
                    size="model_volume",
                    hover_data=['product_model', 'storage_capacity', 'product_condition'],
                    labels={"price": "Prix Demandé (€)", "estimated_resell_profit": "Marge Estimée (€)"},
                    color_discrete_sequence=px.colors.qualitative.Safe
                )
                fig_scatter.add_hline(y=0, line_dash="dash", line_color="grey", line_width=1.5)
                fig_scatter.update_layout(height=400, template="plotly_white", margin=dict(t=10, b=0, l=0, r=0))
                st.plotly_chart(fig_scatter, use_container_width=True)

# ==========================================
# ONGLET 3 : VOLATILITÉ & LIVE TRENDS
# ==========================================
with tab3:
    if not df_filtered.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📊 Étalement des Prix par Plateforme")
            if 'source' in df_filtered.columns and 'price' in df_filtered.columns:
                fig_violin = px.violin(
                    df_filtered, x="source", y="price", color="source",
                    box=True, points=False,
                    color_discrete_sequence=px.colors.qualitative.Pastel,
                    labels={"price": "Prix (€)", "source": "Plateforme"}
                )
                fig_violin.update_layout(height=380, template="plotly_white", showlegend=False, margin=dict(t=10))
                st.plotly_chart(fig_violin, use_container_width=True)
        
        with col2:
            st.markdown("#### 🔔 Écart-Type et Anomalies Métiers (Z-Score)")
            st.caption("Un Z-Score inférieur à -1.5 isole les opportunités statistiquement bradées.")
            
            if 'z_score' in df_filtered.columns:
                fig_hist = px.histogram(
                    df_filtered, x="z_score",
                    color="source" if 'source' in df_filtered.columns else None,
                    marginal="box", nbins=35,
                    color_discrete_sequence=px.colors.qualitative.Set2,
                    labels={"z_score": "Z-Score", "source": "Plateforme"}
                )
                fig_hist.add_vline(x=-1.5, line_dash="dash", line_color="#dc3545", line_width=2)
                fig_hist.update_layout(height=380, template="plotly_white", margin=dict(t=10))
                st.plotly_chart(fig_hist, use_container_width=True)
        
        # Section Évolution Réelle du Marché Live
        st.markdown("#### 📈 Flux du Marché : Évolution du Prix Moyen des Offres")
        st.caption("Suivi des prix réels proposés pour les 5 modèles les plus volumineux du segment.")
        
        if 'timestamp' in df_filtered.columns and 'price' in df_filtered.columns:
            df_trend_base = df_filtered.copy()
            df_trend_base['hour'] = df_trend_base['timestamp'].dt.floor('H')
            
            top_models_live = df_trend_base['product_model'].value_counts().head(5).index.tolist()
            
            if top_models_live and 'Modèle non répertorié' in top_models_live:
                top_models_live.remove('Modèle non répertorié')
                
            if top_models_live:
                df_trend = df_trend_base[df_trend_base['product_model'].isin(top_models_live)]
                df_trend = df_trend.groupby(['hour', 'product_model'])['price'].mean().reset_index()
                
                fig_trend = px.line(
                    df_trend, x="hour", y="price", color="product_model",
                    markers=True,
                    labels={"hour": "Fenêtre Temporelle", "price": "Prix de l'Offre Moyen (€)"},
                    color_discrete_sequence=px.colors.qualitative.Dark2
                )
                fig_trend.update_layout(height=350, template="plotly_white", hovermode='x unified', margin=dict(t=10))
                st.plotly_chart(fig_trend, use_container_width=True)

# ==========================================
# ONGLET 4 : DATA TABLE (MART)
# ==========================================
with tab4:
    st.markdown("#### 📋 Exploration Active du Registre Mart")
    st.caption("Données nettoyées par le pipeline dbt sans distinction de stockage pour le pricing global.")
    
    preferred_cols = [
        'timestamp', 'source', 'category', 'brand', 'product_model', 
        'storage_capacity', 'product_condition', 'title', 'price', 
        'median_model_price', 'estimated_resell_profit', 'z_score', 
        'deal_score', 'operational_status', 'url','processor_tier', 'release_year','statistical_confidence','data_age_hours'
    ]
    
    cols_display = [col for col in preferred_cols if col in df_filtered.columns]
    
    if cols_display:
        display_df = df_filtered[cols_display].copy()
        
        column_config = {
            "url": st.column_config.LinkColumn("🔗 Lien Source"),
            "price": st.column_config.NumberColumn("💶 Prix Demande", format="%.2f €"),
            "median_model_price": st.column_config.NumberColumn("📊 Médiane Modèle", format="%.2f €"),
            "estimated_resell_profit": st.column_config.NumberColumn("💰 Profit Estimé", format="%.2f €"),
            "timestamp": st.column_config.DatetimeColumn("📅 Indexation", format="DD/MM/YYYY HH:mm"),
            "z_score": st.column_config.NumberColumn("📊 Z-Score", format="%.2f")
        }
        
        st.dataframe(
            display_df.sort_values('estimated_resell_profit', ascending=False),
            use_container_width=True,
            height=550,
            hide_index=True,
            column_config=column_config
        )