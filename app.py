import streamlit as st
import pandas as pd
from modules.data_loader import load_and_validate_data
from modules.tab1_emissions import render_tab1
from modules.tab2_optimizer import render_tab2_optimizer
from modules.tab3_executive import render_tab3_executive

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION & ADAPTIVE THEME CSS
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Petrosea EcoLogix",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Petrosea Corporate Eco Design Tokens & Adaptive CSS (Light/Dark Mode Responsive)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Inter Clean Tech Typography */
    .stApp, .stMarkdown, p, label, button, input, select, textarea {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        letter-spacing: -0.015em;
        font-weight: 700;
    }
    
    h1 {
        font-size: 2.0rem !important;
        font-weight: 800 !important;
        color: #005A36 !important;
        letter-spacing: -0.025em !important;
    }
    
    /* Logo Container Petrosea */
    .logo-container {
        background-color: #FFFFFF;
        padding: 12px;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 15px;
        box-shadow: 0 4px 12px rgba(0, 90, 54, 0.08);
        border: 1px solid rgba(0, 90, 54, 0.12);
    }
    
    /* Executive Metric Card Styling - Adaptive Theme Support */
    div[data-testid="stMetric"] {
        border: 1px solid rgba(0, 90, 54, 0.25);
        padding: 12px 16px;
        border-radius: 12px;
        box-shadow: 0 2px 6px rgba(0, 90, 54, 0.05);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    div[data-testid="stMetric"]:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 16px rgba(0, 90, 54, 0.15);
    }
    
    div[data-testid="stMetric"] label {
        font-weight: 600 !important;
        font-size: 0.85rem !important;
    }
    
    div[data-testid="stMetricValue"] {
        font-size: 1.35rem !important;
        font-weight: 700 !important;
        line-height: 1.25 !important;
        word-break: break-word !important;
    }

    /* Status Badges */
    .badge-local { background-color: #00875A; color: #FFFFFF; padding: 4px 12px; border-radius: 12px; font-weight: 700; font-size: 0.85rem; font-family: 'Inter', sans-serif; }
    .badge-national { background-color: #F59E0B; color: #FFFFFF; padding: 4px 12px; border-radius: 12px; font-weight: 700; font-size: 0.85rem; font-family: 'Inter', sans-serif; }
    .badge-inter { background-color: #0284C7; color: #FFFFFF; padding: 4px 12px; border-radius: 12px; font-weight: 700; font-size: 0.85rem; font-family: 'Inter', sans-serif; }
    
    /* Callout Containers - High Contrast Adaptive Color Support */
    .petrosea-callout {
        background-color: rgba(0, 168, 107, 0.12);
        border-left: 5px solid #00A86B;
        padding: 14px 18px;
        border-radius: 8px;
        margin-bottom: 20px;
    }
    
    .petrosea-callout h4 {
        color: #00A86B !important;
        margin-top: 0 !important;
        margin-bottom: 6px !important;
        font-weight: 700 !important;
    }

    .petrosea-callout, .petrosea-callout div, .petrosea-callout p, .petrosea-callout li, .petrosea-callout span, .petrosea-callout b, .petrosea-callout strong {
        color: inherit !important;
    }

    /* Enterprise Tab Navigation Spacing & Visual Hierarchy */
    .stTabs [data-baseweb="tab-list"] {
        gap: 16px !important;
        border-bottom: 2px solid rgba(0, 90, 54, 0.12) !important;
        padding-bottom: 4px !important;
        margin-bottom: 20px !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 44px !important;
        padding: 8px 22px !important;
        border-radius: 8px 8px 0px 0px !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        letter-spacing: -0.01em !important;
        transition: all 0.2s ease !important;
    }

    .stTabs [aria-selected="true"] {
        color: #005A36 !important;
        font-weight: 700 !important;
        border-bottom: 3px solid #005A36 !important;
        background-color: rgba(0, 90, 54, 0.06) !important;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. DATA LOADING & PYDANTIC SCHEMA VALIDATION
# -----------------------------------------------------------------------------
try:
    df_emissions, df_suppliers, df_routes = load_and_validate_data()
except Exception as e:
    st.error(f"File data belum ditemukan di folder data/ — jalankan `python scripts/extract_sr_pdf.py` dulu untuk mengekstrak data dari PDF. Rincian error: {e}")
    st.stop()

# -----------------------------------------------------------------------------
# 3. SIDEBAR BRANDING & DATA DISCLAIMER
# -----------------------------------------------------------------------------
st.sidebar.markdown("""
    <div class="logo-container">
        <img src="https://www.petrosea.com/wp-content/uploads/2023/03/logo-petrosea.png" width="160">
    </div>
""", unsafe_allow_html=True)

st.sidebar.title("🌱 Petrosea EcoLogix")
st.sidebar.caption("Evaluasi emisi & risiko logistik")
st.sidebar.markdown("---")
st.sidebar.info(
    "📄 **Sumber Data**\n\n"
    "Data diekstrak langsung dari Laporan Keberlanjutan PT Petrosea Tbk 2025. "
    "Digunakan untuk mensimulasikan efisiensi biaya dari opsi dekarbonisasi."
)

# -----------------------------------------------------------------------------
# 4. HEADER & KPI OVERVIEW CARDS
# -----------------------------------------------------------------------------
st.title("🌱 Petrosea EcoLogix")
st.caption("Dashboard Dekarbonisasi Rantai Pasok PT Petrosea Tbk")

available_years = sorted(df_emissions['Year'].unique().tolist())
col_hdr1, col_hdr2 = st.columns([6, 4])
with col_hdr1:
    st.markdown("<div style='font-size:0.85rem; font-weight:700; color:#005A36; margin-top:4px;'>📅 Tahun Analisis:</div>", unsafe_allow_html=True)
    selected_year = st.segmented_control(
        "Tahun Analisis",
        options=available_years,
        default=max(available_years),
        label_visibility="collapsed",
        key="main_segmented_year"
    )
    if selected_year is None:
        selected_year = max(available_years)

st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)

curr_data = df_emissions[df_emissions['Year'] == selected_year].iloc[0]

prev_years = df_emissions[df_emissions['Year'] < selected_year]['Year']
if not prev_years.empty:
    prev_year = prev_years.max()
    prev_data = df_emissions[df_emissions['Year'] == prev_year].iloc[0]
else:
    prev_year = selected_year
    prev_data = curr_data

# Header KPI Cards
col1, col2, col3, col4 = st.columns(4)

with col1:
    s1_curr = curr_data.get('Scope1_tCO2e', 0.0)
    s2_curr = curr_data.get('Scope2_tCO2e', 0.0)
    total_emissions = s1_curr + s2_curr
    s1_prev = prev_data.get('Scope1_tCO2e', 0.0)
    s2_prev = prev_data.get('Scope2_tCO2e', 0.0)
    prev_emissions = s1_prev + s2_prev
    diff_emissions = ((total_emissions - prev_emissions) / prev_emissions * 100) if prev_emissions > 0 else 0.0
    badge_text = f"📉 {diff_emissions:.1f}% vs {prev_year}" if diff_emissions <= 0 else f"📈 +{diff_emissions:.1f}% vs {prev_year}"
    
    st.metric(
        label="Emisi langsung alat berat & listrik (Scope 1 & 2)", 
        value=f"{total_emissions:,.2f} tCO2e", 
        delta=badge_text,
        help="Jumlah emisi dari penggunaan bahan bakar solar alat berat tambang dan konsumsi listrik operasional."
    )

with col2:
    scope3_tot = (
        curr_data.get('Scope3_Cat4_UpstreamLogistics_tCO2e', 0.0) + 
        curr_data.get('Scope3_Cat6_BusinessTravel_tCO2e', 0.0) + 
        curr_data.get('Scope3_Cat1_PurchasedGoods_tCO2e', 0.0)
    )
    st.metric(
        label="Emisi rantai pasok & logistik (Scope 3)", 
        value=f"{scope3_tot:,.2f} tCO2e", 
        delta="logistik & barang",
        help="Emisi tidak langsung dari pengiriman barang, transportasi laut/darat, dan pembelian material."
    )

with col3:
    revenue = curr_data.get('Revenue_MUSD', 0.0)
    if revenue and revenue > 0:
        intensity = total_emissions / revenue
        intensity_disp = f"{intensity:.2f} tCO2e/$M"
        st.metric(
            label="Intensitas karbon per pendapatan", 
            value=intensity_disp, 
            delta="tCO2e per $1M pendapatan",
            help="Jumlah emisi Scope 1 & 2 yang dihasilkan untuk setiap 1 juta USD pendapatan korporasi."
        )
    else:
        st.metric(label="Intensitas karbon per pendapatan", value="N/A")

with col4:
    tkdn_val = curr_data.get('TKDN_Percentage', 0.0)
    st.metric(
        label="Tingkat Komponen Dalam Negeri (TKDN)", 
        value=f"{tkdn_val:.1f}%", 
        delta="target minimal 95%",
        help="Persentase penggunaan barang dan jasa dari pemasok lokal/domestik."
    )

st.markdown("---")

# -----------------------------------------------------------------------------
# 5. TAB NAVIGATION & RENDER DISPATCHING (CONSOLIDATED 3-TAB ARCHITECTURE)
# -----------------------------------------------------------------------------
tab1, tab2, tab3 = st.tabs([
    "Profil Emisi", 
    "Simulator Rute", 
    "Laporan Direksi"
])

with tab1:
    render_tab1(df_emissions, df_suppliers, selected_year, scope3_tot, curr_data)

with tab2:
    render_tab2_optimizer(df_routes, curr_data)

with tab3:
    render_tab3_executive(df_emissions, df_suppliers, df_routes, selected_year, scope3_tot, curr_data)

# -----------------------------------------------------------------------------
# 6. CORPORATE FOOTER & DATA PROVENANCE STAMP
# -----------------------------------------------------------------------------
st.markdown("---")