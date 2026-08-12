import streamlit as st
import pandas as pd
import base64
from modules.data_loader import load_and_validate_data
from modules.tab1_emissions import render_tab1
from modules.tab2_optimizer import render_tab2_optimizer
from modules.tab3_executive import render_tab3_executive

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION & ADAPTIVE THEME CSS
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Petrosea EcoLogix",
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
    
    /* Sustainable Corporate Palette - Adaptive via Streamlit Variables */
    
    h1 {
        font-size: 2.0rem !important;
        font-weight: 800 !important;
        letter-spacing: -0.025em !important;
        color: var(--text-color) !important;
    }
    
    /* Logo Container Petrosea */
    .logo-container {
        background-color: var(--secondary-background-color);
        padding: 12px;
        border-radius: 16px;
        text-align: center;
        margin-bottom: 15px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
        border: 1px solid var(--border-color, rgba(0, 90, 54, 0.10));
    }
    
    /* Executive Metric Card Styling (Bento Box Vibe) */
    div[data-testid="stMetric"] {
        background-color: var(--secondary-background-color);
        border: 1px solid var(--border-color, rgba(0, 90, 54, 0.10));
        padding: 16px 20px;
        border-radius: 16px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
    }
    
    div[data-testid="stMetric"]:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 24px rgba(232, 119, 34, 0.12); /* Subtle orange glow on hover */
        border-color: rgba(232, 119, 34, 0.3);
    }
    
    div[data-testid="stMetric"] label {
        font-weight: 600 !important;
        font-size: 0.85rem !important;
        color: var(--text-color) !important;
        opacity: 0.8;
    }
    
    div[data-testid="stMetricValue"] {
        font-size: 1.5rem !important;
        font-weight: 800 !important;
        color: var(--text-color) !important;
        line-height: 1.2 !important;
    }

    /* Status Badges */
    .badge-local { background-color: #005A36; color: #FFFFFF; padding: 4px 12px; border-radius: 12px; font-weight: 700; font-size: 0.85rem; }
    .badge-national { background-color: #E87722; color: #FFFFFF; padding: 4px 12px; border-radius: 12px; font-weight: 700; font-size: 0.85rem; }
    .badge-inter { background-color: #0284C7; color: #FFFFFF; padding: 4px 12px; border-radius: 12px; font-weight: 700; font-size: 0.85rem; }
    
    /* Callout Containers */
    .petrosea-callout {
        background-color: var(--secondary-background-color);
        border-left: 6px solid #E87722; /* Orange accent */
        padding: 16px 20px;
        border-radius: 12px;
        margin-bottom: 20px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.03);
    }
    
    .petrosea-callout h4 {
        color: #E87722 !important;
        margin-top: 0 !important;
        margin-bottom: 8px !important;
        font-weight: 800 !important;
    }
    
    .petrosea-callout p {
        color: var(--text-color) !important;
    }

    /* Enterprise Tab Navigation Spacing & Visual Hierarchy */
    .stTabs [data-baseweb="tab-list"] {
        gap: 16px !important;
        border-bottom: 2px solid var(--border-color, rgba(0, 90, 54, 0.10)) !important;
        padding-bottom: 0px !important;
        margin-bottom: 24px !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 48px !important;
        padding: 8px 24px !important;
        border-radius: 12px 12px 0px 0px !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        color: var(--text-color) !important;
        opacity: 0.7;
        transition: all 0.2s ease !important;
        background-color: transparent !important;
        border: none !important;
    }

    .stTabs [aria-selected="true"] {
        color: var(--text-color) !important;
        opacity: 1.0 !important;
        font-weight: 800 !important;
        border-bottom: 4px solid #E87722 !important; /* Orange underline for active tab */
        background-color: var(--secondary-background-color) !important;
        box-shadow: 0 -4px 12px rgba(0,0,0,0.02) !important;
    }

    /* Hapus manual @media dark mode karena sering bentrok dengan Streamlit Theme Switcher */
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
def get_svg_logo(file_path, width="160px"):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            svg_content = f.read()
        # Remove newlines so Markdown parser doesn't break the HTML block
        svg_content = svg_content.replace('\n', ' ').replace('\r', '')
        # Ensure it has width and height attributes mapped properly for inline display
        if "<svg" in svg_content:
            svg_content = svg_content.replace('<svg', f'<svg style="width: {width}; height: auto;"')
        return svg_content
    except Exception:
        return ""

logo_svg_sidebar = get_svg_logo("assets/logo-ecologix.svg", width="140px")
logo_svg_header = get_svg_logo("assets/logo-ecologix.svg", width="180px")

st.sidebar.markdown(f"""
    <div class="logo-container" style="background: transparent; border: none; box-shadow: none; padding: 0; margin-bottom: 20px;">
        {logo_svg_sidebar}
    </div>
""", unsafe_allow_html=True)

st.sidebar.title("Petrosea EcoLogix")
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
if logo_svg_header:
    st.markdown(f'<div style="margin-bottom: -25px;">{logo_svg_header}</div>', unsafe_allow_html=True)
    st.title("Petrosea EcoLogix")
else:
    st.title("Petrosea EcoLogix")

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
    "Simulator Logistik", 
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
# EcoLogix Final Executive Build & Documentation Sync Stamp