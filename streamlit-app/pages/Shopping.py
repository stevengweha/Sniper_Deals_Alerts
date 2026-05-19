import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

# --- CONFIGURATION ---
st.set_page_config(page_title="Smart Buy Sentinel | Global Analytics", page_icon="🎯", layout="wide")

# Charger les variables depuis le fichier .env si présent
load_dotenv()
DB_URL = os.getenv("DB_URL")
# Connexion à la base de données
engine = create_engine(DB_URL)

@st.cache_data(ttl=300)
def fetch_data():
    df = pd.read_sql("SELECT * FROM public_shopping.final_data", engine)
    
    # Cast des types pour la sécurité
    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    df['pct_deviation'] = pd.to_numeric(df['pct_deviation'], errors='coerce')
    df['estimated_resell_profit'] = pd.to_numeric(df['estimated_resell_profit'], errors='coerce')
    df['z_score'] = pd.to_numeric(df['z_score'], errors='coerce')
    df['market_volume'] = pd.to_numeric(df.get('market_volume', 1), errors='coerce')
    df['median_type_price'] = pd.to_numeric(df.get('median_type_price', 0), errors='coerce')
    df['median_market_price'] = pd.to_numeric(df.get('median_market_price', 0), errors='coerce')
    
    return df.dropna(subset=['price', 'timestamp'])

try:
    df_raw = fetch_data()
except Exception as e:
    st.error(f"Erreur de connexion à la base de données : {e}")
    st.stop()

# --- SIDEBAR FILTERS ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/833/833314.png", width=80)
    st.title("🎯 Paramètres Sentinel")
    st.markdown("---")
    
    categories_available = ['Toutes'] + list(df_raw['category'].dropna().unique())
    selected_category = st.selectbox("📂 Catégorie Globale", categories_available)

    if selected_category != 'Toutes':
        df_category = df_raw[df_raw['category'] == selected_category]
    else:
        df_category = df_raw

    # Ajout d'un filtre adaptatif sur le Type spécifique
    types_available = ['Tous'] + list(df_category['type'].dropna().unique())
    selected_type = st.selectbox("🏷️ Type de produit", types_available)

    if selected_type != 'Tous':
        df_category = df_category[df_category['type'] == selected_type]

    search_query = st.text_input("🔍 Recherche mots-clés", placeholder="Ex: iPhone 13...")
    source_filter = st.multiselect("🛒 Plateformes", df_category['source'].unique(), default=df_category['source'].unique())

    max_price = int(df_category['price'].max() * 1.5) if not df_category.empty else 1000
    price_range = st.slider("💰 Budget Max (€)", 0, max_price, (0, max_price))

if search_query:
    keywords = search_query.lower().split()
    query_mask = df_category['title'].str.lower().apply(lambda x: all(k in x for k in keywords))
else:
    query_mask = True

# Filtrage global
mask = (df_category['source'].isin(source_filter)) & \
       (df_category['price'].between(price_range[0], price_range[1])) & \
       query_mask

df_filtered = df_category[mask].copy()

# --- HEADER STATS ---
category_title = selected_category if selected_category != 'Toutes' else "Toutes les catégories"
st.markdown(f"## 📡 Radar de Marché : `{category_title}`" + (f" > `{selected_type}`" if selected_type != 'Tous' else ""))
st.caption(f"Analyse en temps réel de **{len(df_filtered)}** offres actives correspondant à vos critères.")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Prix Moyen Sélection", f"{df_filtered['price'].mean():.2f} €" if not df_filtered.empty else "N/A")
with col2:
    st.metric("Meilleur Prix", f"{df_filtered['price'].min():.2f} €" if not df_filtered.empty else "N/A")
with col3:
    if not df_filtered.empty and df_filtered['estimated_resell_profit'].max() > 0:
        # Sécurité pour éviter le crash idxmax() si les groupes sont vides ou nuls
        grouped_profit = df_filtered.groupby('source')['estimated_resell_profit'].mean()
        best_source = grouped_profit.idxmax() if not grouped_profit.empty else "N/A"
        st.metric("Plateforme la plus rentable", best_source.upper())
    else:
        st.metric("Plateforme la plus rentable", "N/A")
with col4:
    alerts_count = len(df_filtered[df_filtered['operational_status'].str.contains('SNIPER', na=False)]) if 'operational_status' in df_filtered.columns else 0
    st.metric("🚨 Alertes Sniper", alerts_count)

st.markdown("---")

# --- REGROUPEMENT PAR ONGLETS (TABS) ---
tab1, tab2, tab3, tab4 = st.tabs(["🚀 Top 10 & Actions", "🗺️ Cartographie & Rentabilité", "📈 Tendances & Distributions", "📋 Data Brute"])

# ==========================================
# ONGLET 1 : LE RADAR SNIPER ET LE TOP 10
# ==========================================
with tab1:
    if not df_filtered.empty and df_filtered['estimated_resell_profit'].max() > 0:
        best_deal = df_filtered.loc[df_filtered['estimated_resell_profit'].idxmax()]
        
        st.markdown("### 🎯 Le Deal Parfait (Meilleur ROI basé sur le modèle de Type)")
        c_gauge, c_info = st.columns([1, 2])
        
        with c_gauge:
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = best_deal['estimated_resell_profit'],
                number = {'prefix': "+", 'suffix': " €", 'font': {'size': 40}},
                delta = {'reference': 0, 'position': "bottom", 'font': {'size': 20}},
                title = {'text': "Profit Réel Estimé", 'font': {'size': 24}},
                gauge = {
                    'axis': {'range': [0, max(100, best_deal['estimated_resell_profit'] * 1.5)], 'tickwidth': 1, 'tickcolor': "darkblue"},
                    'bar': {'color': "#00cc96"},
                    'bgcolor': "white",
                    'borderwidth': 2,
                    'bordercolor': "gray",
                    'steps': [
                        {'range': [0, 20], 'color': "#ffebee"},
                        {'range': [20, 50], 'color': "#fff3e0"},
                        {'range': [50, 1000], 'color': "#e8f5e9"}
                    ],
                    'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': best_deal['estimated_resell_profit']}
                }
            ))
            fig_gauge.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig_gauge, use_container_width=True)

        with c_info:
            st.success(f"**🔥 {best_deal.get('deal_score', 'Anomalie détectée')} sur {best_deal['source'].upper()}**")
            st.markdown(f"#### {best_deal['title']}")
            
            c_det1, c_det2 = st.columns(2)
            with c_det1:
                st.write(f"🏷️ **Prix d'achat :** `{best_deal['price']:.2f} €`")
                st.write(f"📊 **Prix médian de son Type (`{best_deal['type']}`) :** `{best_deal['median_type_price']:.2f} €`")
            with c_det2:
                st.write(f"📈 **Z-Score Catégoriel (`{best_deal['category']}`) :** `{best_deal['z_score']}`")
                st.write(f"🛡️ **État :** `{best_deal.get('etat', 'Non précisé')}`")
            
            if best_deal.get('url'):
                st.link_button("⚡ ACCÉDER À L'OFFRE", best_deal['url'], type="primary", use_container_width=True)
    else:
        st.info("Aucune opportunité avec une marge de revente positive n'a été trouvée avec ces filtres.")

    st.markdown("---")
    st.markdown("### 💎 Top 10 des Opportunités (Triées par Marge réelle)")

    if not df_filtered.empty:
        top_deals = df_filtered.sort_values('estimated_resell_profit', ascending=False).head(10)
        
        # Affichage dynamique en grille (2 rangées de 5)
        cols = st.columns(5)
        for i, (index, row) in enumerate(top_deals.iterrows()):
            with cols[i % 5]:
                with st.container(border=True):
                    st.caption(f"🛒 **{row['source'].upper()}** | {row.get('type', '')}")
                    title_short = (row['title'][:40] + '...') if len(str(row['title'])) > 40 else row['title']
                    st.markdown(f"**{title_short}**")
                    st.markdown(f"### {row['price']:.2f} €")
                    
                    if row['estimated_resell_profit'] > 0:
                        st.markdown(f"🟩 **Gain : +{row['estimated_resell_profit']:.2f} €**")
                    else:
                        st.markdown(f"🟥 **Gain : {row['estimated_resell_profit']:.2f} €**")
                    
                    if row.get('url'):
                        st.link_button("Voir", row['url'], use_container_width=True)
                    st.caption(f"Score: {row.get('deal_score', 'N/A')}")

# ==========================================
# ONGLET 2 : CARTOGRAPHIE DU MARCHÉ
# ==========================================
with tab2:
    if not df_filtered.empty:
        c1, c2 = st.columns(2)
        
        with c1:
            st.subheader("🗺️ Treemap : Volumes globaux et Marges")
            st.caption("Taille des cases = Volume de la catégorie globale. Couleur = Marge générée.")
            df_tree = df_filtered.fillna({'category': 'Non classé', 'type': 'Inconnu', 'source': 'Autre'})
            fig_tree = px.treemap(
                df_tree, 
                path=['category', 'type', 'source'], 
                color='estimated_resell_profit',
                color_continuous_scale='RdYlGn',
                color_continuous_midpoint=0,
                values='market_volume'
            )
            fig_tree.update_layout(height=400, margin=dict(t=30, l=10, r=10, b=10))
            st.plotly_chart(fig_tree, use_container_width=True)

        with c2:
            st.subheader("🎯 Matrice des Deals : Achat vs Revente par Type")
            st.caption("Objectif : Ciblez le coin supérieur gauche (Prix d'achat bas, marge forte).")
            fig_scatter = px.scatter(
                df_filtered, 
                x="price", y="estimated_resell_profit", 
                color="source", 
                size=df_filtered['market_volume'].clip(lower=1, upper=50) * 2, 
                hover_data=['title', 'type', 'z_score'],
                labels={"price": "Prix d'achat (€)", "estimated_resell_profit": "Marge estimée (€)"},
                template="plotly_white"
            )
            fig_scatter.add_hline(y=0, line_dash="dash", line_color="red", annotation_text="Seuil de rentabilité")
            fig_scatter.update_layout(height=400, margin=dict(t=30, l=10, r=10, b=10))
            st.plotly_chart(fig_scatter, use_container_width=True)

        c3, c4 = st.columns(2)
        
        with c3:
            st.subheader("📊 Marge Moyenne par Type de Produit")
            st.caption("Quels types précis affichent les plus gros écarts de rentabilité ?")
            df_profit_type = df_filtered.groupby('type')['estimated_resell_profit'].mean().reset_index()
            fig_bar = px.bar(
                df_profit_type.sort_values('estimated_resell_profit', ascending=False).head(15), 
                x='type', y='estimated_resell_profit', 
                color='type', text_auto='.2f',
                labels={"estimated_resell_profit": "Marge Moyenne (€)", "type": ""},
                template="plotly_white"
            )
            fig_bar.update_layout(height=350, showlegend=False)
            st.plotly_chart(fig_bar, use_container_width=True)

        with c4:
            st.subheader("🍩 Densité des Plateformes par Catégorie")
            fig_sun = px.sunburst(
                df_tree, 
                path=['source', 'category'], 
                color='source',
                template="plotly_white"
            )
            fig_sun.update_layout(height=350, margin=dict(t=10, l=10, r=10, b=10))
            st.plotly_chart(fig_sun, use_container_width=True)
            
    else:
        st.info("Données insuffisantes pour générer la cartographie.")

# ==========================================
# ONGLET 3 : TENDANCES & DISTRIBUTIONS
# ==========================================
with tab3:
    if not df_filtered.empty:
        df_filtered['hour'] = df_filtered['timestamp'].dt.floor('H')
        
        c5, c6 = st.columns(2)
        
        with c5:
            st.subheader("📈 Dynamique de Flux")
            st.caption("Volume de détection d'annonces fraîches par heure")
            df_vol = df_filtered.groupby(['hour', 'source']).size().reset_index(name='count')
            fig_vol = px.area(df_vol, x="hour", y="count", color="source", template="plotly_white")
            fig_vol.update_layout(height=350, legend_title_text='Plateforme')
            st.plotly_chart(fig_vol, use_container_width=True)

        with c6:
            st.subheader("📉 Stabilité Temporelle du Prix de Catégorie")
            st.caption("Suivi de l'évolution de l'indice de prix de la catégorie")
            if 'median_market_price' in df_filtered.columns:
                df_med = df_filtered.groupby(['hour', 'category'])['median_market_price'].mean().reset_index()
                fig_med = px.line(df_med, x="hour", y="median_market_price", color="category", markers=True, template="plotly_white")
                fig_med.update_layout(height=350, legend_title_text='Catégorie')
                st.plotly_chart(fig_med, use_container_width=True)
            else:
                st.warning("Indicateur temporel indisponible.")

        c7, c8 = st.columns(2)

        with c7:
            st.subheader("Violin Plot des Prix")
            st.caption("Dispersion fine des prix d'achat par plateforme")
            fig_violin = px.violin(
                df_filtered, x="source", y="price", color="source", 
                box=True, points="all", hover_data=['title', 'type'],
                template="plotly_white"
            )
            fig_violin.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig_violin, use_container_width=True)

        with c8:
            st.subheader("🔔 Spectre de distribution du Z-Score")
            st.caption("Analyse de la masse critique. La zone à gauche de la ligne verte rassemble les réelles pépites de la catégorie.")
            fig_hist = px.histogram(
                df_filtered, x="z_score", color="source", 
                marginal="box", nbins=40,
                labels={"z_score": "Z-Score Catégoriel"},
                template="plotly_white"
            )
            fig_hist.add_vline(x=-1.5, line_dash="dash", line_color="green", annotation_text="Zone Anomalie")
            fig_hist.update_layout(height=400)
            st.plotly_chart(fig_hist, use_container_width=True)
    else:
         st.info("Données temporelles insuffisantes.")

# ==========================================
# ONGLET 4 : EXPLORATION DES DONNÉES BRUTES
# ==========================================
with tab4:
    st.subheader("📋 Base de données Sentinel interactive")
    st.caption("Restitution complète et intègre issue de dbt.")
    
    # Intégration complète de la colonne type et median_type_price
    cols_to_show = ['timestamp', 'source', 'category', 'type', 'title', 'price', 'median_type_price', 'estimated_resell_profit', 'z_score', 'market_volume', 'url']
    existing_cols = [c for c in cols_to_show if c in df_filtered.columns]
    
    st.dataframe(
        df_filtered[existing_cols].sort_values('estimated_resell_profit', ascending=False), 
        use_container_width=True,
        height=600,
        hide_index=True,
        column_config={
            "url": st.column_config.LinkColumn("Lien d'achat"),
            "price": st.column_config.NumberColumn("Prix d'achat", format="%.2f €"),
            "median_type_price": st.column_config.NumberColumn("Médiane Type", format="%.2f €"),
            "estimated_resell_profit": st.column_config.NumberColumn("Marge Estimée", format="%.2f €"),
            "timestamp": st.column_config.DatetimeColumn("Détection", format="DD/MM/YYYY HH:mm"),
            "z_score": st.column_config.NumberColumn("Z-Score", format="%.2f")
        }
    )