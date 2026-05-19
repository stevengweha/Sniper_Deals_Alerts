import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine
import numpy as np

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="SNCF Sentinel - Dashboard Expert",
    page_icon="🚆",
    layout="wide"
)

# Style CSS Premium Dark
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #adbac7; }
    .stMetric { 
        background-color: #1c2128; 
        padding: 20px; 
        border-radius: 12px; 
        border: 1px solid #30363d;
        border-left: 5px solid #2f81f7;
    }
    .legend-box {
        padding: 15px;
        background-color: #161b22;
        border-radius: 10px;
        border: 1px solid #30363d;
        font-size: 0.9rem;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CONNEXION ET CHARGEMENT ---
@st.cache_resource
def get_engine():
    return create_engine("postgresql://admin:admin@postgres_data:5432/smart_buy_db")

@st.cache_data(ttl=3600)
def load_data():
    engine = get_engine()
    df = pd.read_sql("SELECT * FROM public_transport.mart_transport_final", engine)
    df['annee'] = df['annee'].astype(int)
    df = df[(df['annee'] >= 2018) & (df['annee'] <= 2024)]
    return df

try:
    df_all = load_data()
except Exception as e:
    st.error(f"❌ Erreur de base de données : {e}")
    st.stop()

# --- 3. BARRE LATÉRALE ---
st.sidebar.header("🕹️ Pilotage Stratégique")

years = sorted(df_all['annee'].unique().tolist(), reverse=True)
selected_year = st.sidebar.selectbox("📅 Période d'analyse", ["Toutes les années"] + [str(y) for y in years])

segments = sorted(df_all['segmentation_marketing'].unique().tolist())
selected_segments = st.sidebar.multiselect("🚉 Segments de gares", segments, default=segments)

# --- 4. LOGIQUE DE FILTRAGE ---
mask_seg = df_all['segmentation_marketing'].isin(selected_segments)

if selected_year == "Toutes les années":
    df_filtered = df_all[mask_seg].copy()
    # Agrégation par gare pour les visuels de classement
    df_display = df_filtered.groupby('gare_depart').agg({
        'ponctualite_annuelle': 'mean',
        'flux_voyageurs': 'sum',
        'total_retards_an': 'sum',
        'indice_nuisance_moyen': 'mean',
        'cause_principale': lambda x: x.mode()[0] if not x.empty else "N/A",
        'statut_ligne': lambda x: x.mode()[0] if not x.empty else "N/A"
    }).reset_index()
    title_suffix = "Historique (2018-2024)"
else:
    df_display = df_all[mask_seg & (df_all['annee'] == int(selected_year))].copy()
    title_suffix = f"Année {selected_year}"

# --- 5. HEADER & KPI ---
st.title(f"🚆 Sentinel Analytics : {title_suffix}")

k1, k2, k3, k4 = st.columns(4)
with k1:
    val = df_display['ponctualite_annuelle'].mean()
    st.metric("Ponctualité Réseau", f"{val:.1f}%", delta=f"{val-90:.1f}% vs Objectif")
with k2:
    st.metric("Flux Total voyageurs", f"{df_display['flux_voyageurs'].sum():,.0f} ")
with k3:
    st.metric("Retards Cumulés", f"{int(df_display['total_retards_an'].sum()):,}")
with k4:
    st.metric("Score Nuisance", f"{df_display['indice_nuisance_moyen'].mean():.2f}")

st.divider()

# --- 6. ANALYSE 1 : ÉVOLUTION DU TRAFIC (DEMANDE UTILISATEUR) ---
st.header("📈 Évolution du Trafic vs Ponctualité")
evol_df = df_all[mask_seg].groupby('annee').agg({
    'flux_voyageurs': 'sum',
    'ponctualite_annuelle': 'mean'
}).reset_index()

fig_evol = go.Figure()
fig_evol.add_trace(go.Bar(x=evol_df['annee'], y=evol_df['flux_voyageurs'], name="Voyageurs", marker_color='#2f81f7', opacity=0.6))
fig_evol.add_trace(go.Scatter(x=evol_df['annee'], y=evol_df['ponctualite_annuelle'], name="Ponctualité %", yaxis="y2", line=dict(color='#f85149', width=4)))

fig_evol.update_layout(
    yaxis=dict(title="Volume de Voyageurs"),
    yaxis2=dict(title="Ponctualité (%)", overlaying="y", side="right", range=[80, 100]),
    legend=dict(x=0.01, y=0.99),
    hovermode="x unified",
    height=400
)
st.plotly_chart(fig_evol, use_container_width=True)

st.divider()

# --- 7. ANALYSE 2 : CLASSEMENTS (HALL OF SHAME) ---
st.header("🚩 Qui arrive le plus en retard ?")
col_vol, col_nui = st.columns(2)

with col_vol:
    st.subheader("Gares cumulant le plus de retards (Volume)")
    top_v = df_display.nlargest(10, 'total_retards_an')
    fig_v = px.bar(top_v, x='total_retards_an', y='gare_depart', orientation='h', color='total_retards_an', color_continuous_scale='Reds', text_auto=True)
    st.plotly_chart(fig_v, use_container_width=True)

with col_nui:
    st.subheader("Top Nuisance (Impact Passagers)")
    top_n = df_display.nlargest(10, 'indice_nuisance_moyen')
    fig_n = px.bar(top_n, x='indice_nuisance_moyen', y='gare_depart', orientation='h', color='indice_nuisance_moyen', color_continuous_scale='Purples', text_auto='.2f')
    st.plotly_chart(fig_n, use_container_width=True)

st.divider()

# --- 8. ANALYSE 3 : MATRICE D'IMPACT (TREEMAP & SCATTER) ---
st.header("🎯 Matrice d'Impact Social")
col_tree, col_drift = st.columns([2, 1])

with col_tree:
    st.subheader("Cartographie Flux / Ponctualité")
    fig_tree = px.treemap(df_display, path=['gare_depart'], values='flux_voyageurs',
                          color='ponctualite_annuelle', color_continuous_scale='RdYlGn', color_continuous_midpoint=90)
    st.plotly_chart(fig_tree, use_container_width=True)

with col_drift:
    st.subheader("Dérive par Segment")
    drift_data = df_all[mask_seg].groupby(['annee', 'segmentation_marketing'])['ponctualite_annuelle'].mean().unstack()
    fig_heat = px.imshow(drift_data, text_auto=".1f", color_continuous_scale='RdYlGn')
    st.plotly_chart(fig_heat, use_container_width=True)

# Row 4: Corrélations
st.divider()
c_scat, c_pie = st.columns(2)
with c_scat:
    st.subheader("🔍 Corrélation : Flux vs Retards")
    fig_scat = px.scatter(df_display, x='flux_voyageurs', y='ponctualite_annuelle', size='total_retards_an', color='cause_principale', log_x=True, hover_name='gare_depart')
    st.plotly_chart(fig_scat, use_container_width=True)
with c_pie:
    st.subheader("🧩 Responsabilité des Retards")
    fig_sun = px.sunburst(df_display, path=['statut_ligne', 'cause_principale'], values='total_retards_an', color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig_sun, use_container_width=True)

# --- ANALYSE AVANCÉE : LE PARADOXE DE MONTPARNASSE ---
st.divider()
st.header("🔬 Analyse de Corrélation : Volume vs Performance")

# Préparation des données pour le croisement
df_corr = df_display.copy()
# On calcule un ratio de "Probabilité individuelle de retard"
df_corr['probabilite_retard'] = (df_corr['total_retards_an'] / df_corr['flux_voyageurs']) * 100

c_left, c_right = st.columns([2, 1])

with c_left:
    fig_paradox = px.scatter(
        df_corr, 
        x='total_retards_an', 
        y='ponctualite_annuelle',
        size='flux_voyageurs', 
        color='indice_nuisance_moyen',
        hover_name='gare_depart',
        labels={'total_retards_an': 'Nombre total de retards (Brut)', 'ponctualite_annuelle': 'Taux de Ponctualité (%)'},
        title="Pourquoi Montparnasse est en haut à droite ?"
    )
    # Ajouter une ligne de moyenne
    fig_paradox.add_hline(y=df_corr['ponctualite_annuelle'].mean(), line_dash="dot", annotation_text="Moyenne Nationale")
    st.plotly_chart(fig_paradox, use_container_width=True)

with c_right:
    st.markdown("""
    <div class='legend-box'>
    <b>💡 Explication du croisement :</b><br><br>
    - <b>Axe horizontal (Retards) :</b> Plus on va à droite, plus le <u>nombre</u> de trains en retard est élevé (Montparnasse est ici).<br>
    - <b>Axe vertical (Performance) :</b> Plus on monte, meilleur est le <u>service</u> perçu par le voyageur.<br><br>
    <b>Le cas Montparnasse :</b> Elle est très à droite (beaucoup de retards) mais reste haute (bonne ponctualité %). C'est le signe d'un hub <b>saturé mais bien géré</b>.
    </div>
    """, unsafe_allow_html=True)

# --- ANALYSE PAR SEGMENT (LGV vs VILLE) ---
st.subheader("🚠 Performance par Typologie de Gare")
fig_box = px.box(
    df_all if selected_year == "Toutes les années" else df_display, 
    x='segmentation_marketing', 
    y='ponctualite_annuelle', 
    color='segmentation_marketing',
    points="all",
    title="Dispersion de la ponctualité par type de gare"
)
st.plotly_chart(fig_box, use_container_width=True)

# --- 9. EXPLORATEUR ---
st.divider()
with st.expander("📂 Consulter la base de données enrichie (Mart Layer)"):
    st.dataframe(df_display.sort_values('total_retards_an', ascending=False), use_container_width=True)

st.caption("SNCF Sentinel v5.0 | Fusion Complète : Flux, Retards, Nuisance et Dérives.")