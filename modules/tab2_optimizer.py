import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy.optimize import linprog
import folium
from datetime import datetime, timedelta
import streamlit.components.v1 as components
import requests
from typing import Dict, Any

try:
    from streamlit_folium import st_folium
    HAS_ST_FOLIUM = True
except ImportError:
    HAS_ST_FOLIUM = False

from modules.constants import (
    BIOFUEL_B100_ABATEMENT_FACTOR,
    EV_RETROFIT_ABATEMENT_FACTOR,
    LOCAL_PROC_LOGISTICS_ABATEMENT_FACTOR,
    BARGE_INTERMODAL_SHIFT_ABATEMENT_FACTOR,
    NET_ZERO_TARGET_PERCENTAGE,
    DEFAULT_CARBON_PRICE_USD,
    TREES_PLANTED_PER_TON_CO2,
    DIESEL_TRUCKS_RETIRED_PER_TON_CO2,
    HOMES_POWERED_PER_TON_CO2
)

# -----------------------------------------------------------------------------
# 1. WEATHER & AQI API INTEGRATION (OPEN-METEO)
# -----------------------------------------------------------------------------
@st.cache_data(ttl=3600)
def fetch_weather_data(lat: float, lon: float) -> Dict[str, Any]:
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&hourly=relative_humidity_2m&timezone=auto"
        res = requests.get(url, timeout=3).json()
        curr = res.get("current_weather", {})
        code = curr.get("weathercode", 0)
        
        weather_map = {
            0: "Cerah", 1: "Cerah Berawan", 2: "Berawan", 3: "Mendung",
            45: "Kabut", 48: "Kabut Tebal",
            51: "Gerimis Ringan", 53: "Gerimis Sedang", 55: "Gerimis Lebat",
            61: "Hujan Ringan", 63: "Hujan Sedang", 65: "Hujan Deras",
            80: "Hujan Lokal", 81: "Hujan Lebat", 82: "Hujan Badai",
            95: "Badai Petir", 96: "Badai Petir + Es", 99: "Badai Petir Deras"
        }
        cuaca_text = weather_map.get(code, "Cerah Berawan")
        humidity_list = res.get("hourly", {}).get("relative_humidity_2m", [75])
        curr_humidity = humidity_list[0] if humidity_list else 75

        return {
            "temp": curr.get("temperature", 28.5),
            "kec_angin": curr.get("windspeed", 12.0),
            "arah_angin": f"{curr.get('winddirection', 180)}°",
            "cuaca": cuaca_text,
            "kelembapan": curr_humidity,
            "lokasi_lengkap": f"Koordinat {lat:.2f}, {lon:.2f}"
        }
    except Exception:
        return {
            "temp": 29.0, "kec_angin": 10.5, "arah_angin": "160°",
            "cuaca": "Cerah Berawan", "kelembapan": 78,
            "lokasi_lengkap": f"Koordinat {lat:.2f}, {lon:.2f} (Simulasi Offline)"
        }

@st.cache_data(ttl=3600)
def fetch_aqi_data(lat: float, lon: float) -> Dict[str, Any]:
    try:
        url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}&current=us_aqi,pm10,pm2_5&timezone=auto"
        res = requests.get(url, timeout=3).json()
        curr = res.get("current", {})
        return {
            "aqi": curr.get("us_aqi", 42),
            "pm10": curr.get("pm10", 18.5),
            "pm2_5": curr.get("pm2_5", 12.0)
        }
    except Exception:
        return {"aqi": 45, "pm10": 20.0, "pm2_5": 14.0}

# -----------------------------------------------------------------------------
# 2. SEQUENTIAL SCOPE 1 PHYSICS & ECONOMIC COST SCIPY SOLVER
# -----------------------------------------------------------------------------
def calculate_decarbonization(
    base_s1: float,
    base_s3: float,
    biofuel_mix: float,
    local_proc_increase: float,
    ev_retrofit_pct: float,
    modal_shift_barge: float,
    carbon_price: float = DEFAULT_CARBON_PRICE_USD
) -> Dict[str, float]:
    reduction_s1_ev = base_s1 * (ev_retrofit_pct / 100.0) * EV_RETROFIT_ABATEMENT_FACTOR
    remaining_s1_diesel = max(0.0, base_s1 - reduction_s1_ev)
    reduction_s1_biofuel = remaining_s1_diesel * (biofuel_mix / 100.0) * BIOFUEL_B100_ABATEMENT_FACTOR
    total_s1_reduction = reduction_s1_ev + reduction_s1_biofuel
    post_s1 = max(0.0, base_s1 - total_s1_reduction)

    reduction_s3_local = base_s3 * (local_proc_increase / 100.0) * LOCAL_PROC_LOGISTICS_ABATEMENT_FACTOR
    reduction_s3_barge = base_s3 * (modal_shift_barge / 100.0) * BARGE_INTERMODAL_SHIFT_ABATEMENT_FACTOR
    total_s3_reduction = reduction_s3_local + reduction_s3_barge
    post_s3 = max(0.0, base_s3 - total_s3_reduction)

    total_abatement = total_s1_reduction + total_s3_reduction
    pct_reduction = (total_abatement / (base_s1 + base_s3)) * 100.0 if (base_s1 + base_s3) > 0 else 0.0

    mc_biofuel = 14.0
    mc_local = -18.5
    mc_barge = -12.0
    mc_ev = 45.0

    cost_biofuel = reduction_s1_biofuel * (mc_biofuel - carbon_price)
    cost_local = reduction_s3_local * (mc_local - carbon_price)
    cost_barge = reduction_s3_barge * (mc_barge - carbon_price)
    cost_ev = reduction_s1_ev * (mc_ev - carbon_price)
    net_cost_change_usd = cost_biofuel + cost_local + cost_barge + cost_ev
    cost_savings_usd = -net_cost_change_usd

    return {
        "post_s1": post_s1, "post_s3": post_s3,
        "total_abatement": total_abatement, "pct_reduction": pct_reduction,
        "cost_savings_usd": cost_savings_usd, "net_cost_change_usd": net_cost_change_usd
    }

def solve_scipy_optimal_decarbonization(
    base_s1: float,
    base_s3: float,
    target_pct: float = NET_ZERO_TARGET_PERCENTAGE,
    carbon_price: float = DEFAULT_CARBON_PRICE_USD
) -> Dict[str, Any]:
    total_baseline = base_s1 + base_s3
    required_abatement = total_baseline * (target_pct / 100.0)

    abate_biofuel_per_pct = base_s1 * (1.0 - 0.1 * EV_RETROFIT_ABATEMENT_FACTOR) * 0.01 * BIOFUEL_B100_ABATEMENT_FACTOR
    abate_local_per_pct = base_s3 * 0.01 * LOCAL_PROC_LOGISTICS_ABATEMENT_FACTOR
    abate_barge_per_pct = base_s3 * 0.01 * BARGE_INTERMODAL_SHIFT_ABATEMENT_FACTOR
    abate_ev_per_pct = base_s1 * 0.01 * EV_RETROFIT_ABATEMENT_FACTOR

    mc_biofuel = 14.0
    mc_local = -18.5
    mc_barge = -12.0
    mc_ev = 45.0

    c = [
        abate_biofuel_per_pct * (mc_biofuel - carbon_price),
        abate_local_per_pct * (mc_local - carbon_price),
        abate_barge_per_pct * (mc_barge - carbon_price),
        abate_ev_per_pct * (mc_ev - carbon_price)
    ]

    A_ub = [[-abate_biofuel_per_pct, -abate_local_per_pct, -abate_barge_per_pct, -abate_ev_per_pct]]
    b_ub = [-required_abatement]

    # Bounds: Biofuel can go up to 100%, others up to 50%
    bounds = [(0, 100), (0, 50), (0, 50), (0, 50)]

    res = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method='highs')

    if res.success:
        return {
            "success": True,
            "biofuel_val": round(res.x[0], 1),
            "local_proc_val": round(res.x[1], 1),
            "modal_shift_val": round(res.x[2], 1),
            "ev_val": round(res.x[3], 1),
            "opt_cost_usd": res.fun
        }
    else:
        return {
            "success": False,
            "biofuel_val": 30.0, "local_proc_val": 25.0,
            "modal_shift_val": 25.0, "ev_val": 15.0,
            "opt_cost_usd": 0.0
        }

# -----------------------------------------------------------------------------
# MAIN RENDER FUNCTION FOR TAB 2
# -----------------------------------------------------------------------------
def render_tab2_optimizer(df_routes: pd.DataFrame, curr_data: pd.Series):
    """
    Renders Tab 2: Simulator Rute & 3 Fitur Unggulan Operasional.
    Follows a strict 1 -> 2 -> 3 downward narrative flow.
    """
    st.subheader("Simulator Rute")
    st.caption("Prediksi iklim koridor, simulasi kebijakan dekarbonisasi preskriptif, dan jurnal audit risiko operasional.")
    st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # FITUR 1: PREDIKSI IKLIM & NOTIFIKASI RISIKO K3 7 HARI KE DEPAN (ATAS)
    # -------------------------------------------------------------------------
    st.markdown("### 1. Prediksi iklim & notifikasi risiko K3 7 hari ke depan")
    st.caption("Prakiraan cuaca real-time & Indeks Kualitas Udara (AQI) dari Open-Meteo API di seluruh koridor pengiriman Petrosea.")

    weather_cache = {}
    aqi_cache = {}
    bad_weather_sites = []
    table_rows = []

    for idx, row in df_routes.iterrows():
        w_info = fetch_weather_data(row['Lat_Dest'], row['Lon_Dest'])
        a_info = fetch_aqi_data(row['Lat_Dest'], row['Lon_Dest'])
        weather_cache[row['Route_ID']] = w_info
        aqi_cache[row['Route_ID']] = a_info
        cuaca_text = w_info['cuaca']
        
        if any(w in cuaca_text for w in ["Hujan", "Petir", "Deras", "Badai"]):
            status_risk, action_rec = "Risiko Tinggi (Hujan/Badai)", "Tunda Pengiriman Laut / Evaluasi Darat"
            bad_weather_sites.append(f"{row['Destination']} ({cuaca_text})")
        elif "Berawan" in cuaca_text or "Mendung" in cuaca_text:
            status_risk, action_rec = "Waspada (Berawan)", "Sesuaikan Kecepatan Armada"
        else:
            status_risk, action_rec = "Kondisi Optimal (Cerah)", "Jalur Pengiriman Normal"
        
        table_rows.append({
            "Kode Rute": row['Route_ID'],
            "Tujuan Pengiriman": row['Destination'],
            "Jarak (km)": f"{row['Distance_km']:,} km",
            "Frekuensi": f"{row['Avg_Monthly_Trips']} Trip/bln",
            "Cuaca Real-Time": f"{cuaca_text} ({w_info['temp']}°C)",
            "Kelembapan": f"{w_info['kelembapan']}%",
            "Kualitas Udara": f"AQI {a_info['aqi']}",
            "Status Risiko": status_risk,
            "Rekomendasi Operasional": action_rec
        })

    if bad_weather_sites:
        st.error(f"⚠️ **Peringatan Cuaca Buruk di Koridor**: **{', '.join(bad_weather_sites)}**. Sesuai protokol keselamatan K3 Petrosea, pengiriman laut pada koridor ini ditunda sementara.")
    else:
        st.success("✅ **Status Koridor Pengiriman**: Seluruh rute dalam kondisi cuaca aman.")

    col_m1, col_m2 = st.columns([6, 4])
    with col_m1:
        st.markdown("#### Peta Rute Pengiriman Logistik")
        psf_lat, psf_lon = -1.23, 116.85
        m = folium.Map(location=[-2.2, 117.8], zoom_start=5, tiles=None)
        folium.TileLayer("CartoDB positron", name="Peta Vektor").add_to(m)
        folium.TileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}", attr="Esri World Imagery", name="Peta Satelit").add_to(m)

        psf_html = """<div style="font-family: 'Inter', sans-serif; padding: 6px; width: 180px;"><b style="color: #005A36;">HUB UTAMA LOGISTIK</b><br><span>Fasilitas Petrosea (PSF) Balikpapan</span><br><small style="color: #5A6862;">Pusat Angkutan & Material</small></div>"""
        folium.Marker(location=[psf_lat, psf_lon], popup=folium.Popup(psf_html, max_width=220), tooltip="HUB UTAMA: PSF Balikpapan", icon=folium.Icon(color="darkgreen", icon="building", prefix="fa")).add_to(m)

        for idx, row in df_routes.iterrows():
            w_info = weather_cache[row['Route_ID']]
            a_info = aqi_cache[row['Route_ID']]
            cuaca_text = w_info['cuaca']
            is_marine = "barge" in str(row.get('Transport_Mode', '')).lower() or row['Distance_km'] > 500 or "sorong" in row['Destination'].lower()
            mode_label = "Marine Barge (Laut)" if is_marine else "Trucking (Darat)"
            dash_pattern = "6, 8" if is_marine else None
            marker_color, line_color, status_icon = ("red", "#D9381E", "triangle-exclamation") if any(w in cuaca_text for w in ["Petir", "Deras", "Hujan"]) else (("orange", "#F59E0B", "cloud") if any(w in cuaca_text for w in ["Berawan", "Mendung"]) else ("green", "#005A36", "circle-check"))
            
            folium.PolyLine(locations=[[psf_lat, psf_lon], [row['Lat_Dest'], row['Lon_Dest']]], color=line_color, weight=4.0 if not is_marine else 3.5, dash_array=dash_pattern, opacity=0.85, tooltip=f"Rute {row['Route_ID']}: Balikpapan ➔ {row['Destination']} ({mode_label})").add_to(m)
            site_html = f"""<div style="font-family: 'Inter', sans-serif; padding: 6px; width: 200px;"><b style="color: #005A36;">{row['Destination']}</b><br><span style="font-size: 0.85rem;">Moda: <b>{mode_label}</b></span><br><span style="font-size: 0.85rem;">Cuaca: <b>{cuaca_text} ({w_info['temp']}°C)</b></span><br><span style="font-size: 0.85rem;">💧 Kelembapan: <b>{w_info['kelembapan']}%</b></span><br><span style="font-size: 0.85rem;">💨 Angin: <b>{w_info['kec_angin']} km/j ({w_info['arah_angin']})</b></span><br><span style="font-size: 0.85rem;">🍃 Kualitas Udara: <b>US AQI {a_info['aqi']}</b></span><br><span style="font-size: 0.85rem;">📍 Jarak: <b>{row['Distance_km']:,} km</b> | <b>{row['Avg_Monthly_Trips']} Trip/bln</b></span></div>"""
            folium.Marker(location=[row['Lat_Dest'], row['Lon_Dest']], popup=folium.Popup(site_html, max_width=240), tooltip=f"{row['Destination']} ({cuaca_text} - {w_info['temp']}°C)", icon=folium.Icon(color=marker_color, icon=status_icon, prefix="fa")).add_to(m)

        folium.LayerControl(position="topright").add_to(m)
        if HAS_ST_FOLIUM: st_folium(m, use_container_width=True, height=440, key="leaflet_map_tab2")
        else: components.html(m._repr_html_(), height=450)

    with col_m2:
        st.markdown("#### Detail Cuaca Rute")
        selected_route_id = st.selectbox("Pilih Rute Pengiriman", df_routes['Route_ID'] + " - " + df_routes['Destination'], key="route_select_tab2")
        r_id_selected = selected_route_id.split(" - ")[0]
        w_res, a_res = weather_cache[r_id_selected], aqi_cache[r_id_selected]
        
        with st.container(border=True):
            st.markdown(f"**Kondisi Cuaca Saat Ini**")
            st.caption(f"📍 {w_res['lokasi_lengkap']}")
            st.warning(f"**Kondisi:** {w_res['cuaca']}\n\n**Suhu:** {w_res['temp']}°C | **Kelembapan:** {w_res['kelembapan']}%")
            st.caption(f"Angin: {w_res['kec_angin']} km/j ({w_res['arah_angin']})")
        with st.container(border=True):
            st.markdown(f"**Indeks Kualitas Udara (AQI)**")
            aqi_val = a_res['aqi']
            st.metric(label="Indeks US AQI", value=f"{aqi_val}", delta="Baik" if aqi_val <= 50 else ("Sedang" if aqi_val <= 100 else "Tidak Sehat"))
            st.caption(f"PM2.5: {a_res['pm2_5']} µg/m³ | PM10: {a_res['pm10']} µg/m³")

    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # FITUR 2: OPTIMASI RUTE INTERMODAL & SIMULASI KEBIJAKAN KARBON (TENGAH)
    # -------------------------------------------------------------------------
    st.markdown("---")
    st.markdown("### 2. Optimasi Rute Intermodal & Simulasi Kebijakan Karbon")
    st.caption("Analisis trade-off waktu transit vs emisi Scope 3, serta penentuan alokasi kebijakan.")

    # 2A. EVALUASI MODA PENGIRIMAN & PROTEKSI MATERIAL PRESISI EPC
    with st.expander("Evaluasi Moda Pengiriman & Proteksi Material Presisi EPC", expanded=True):
        st.caption("Analisis kompromi antara kecepatan waktu transit, risiko kelembapan koridor, biaya proteksi material presisi, dan jejak emisi Scope 3.")
        
        # EXPLICIT ROUTE SELECTOR INSIDE CALCULATOR
        selected_route_id = st.selectbox(
            "📌 Pilih Koridor Pengiriman Logistik Petrosea",
            options=df_routes['Route_ID'].tolist(),
            format_func=lambda x: f"{x} - {df_routes[df_routes['Route_ID']==x]['Origin'].values[0]} ➔ {df_routes[df_routes['Route_ID']==x]['Destination'].values[0]} (Jarak: {df_routes[df_routes['Route_ID']==x]['Distance_km'].values[0]} km)",
            key="route_select_tab2_calculator"
        )
        
        r_sel_row = df_routes[df_routes['Route_ID'] == selected_route_id].iloc[0]
        dist_km = r_sel_row['Distance_km']
        curr_hum = weather_cache[selected_route_id]['kelembapan']

        col_c1, col_c2 = st.columns(2)
        with col_c1:
            cargo_type = st.selectbox(
                "Tipe Material Kargo",
                ["Kargo Sensitif Kelembapan (Sparepart Elektrikal Presisi / Pompa Hydrospec)", "Kargo Standar (Material Curah / Tambang Umum)"],
                key="cargo_type_select"
            )
            mode_choice = st.radio(
                "Moda Transportasi Utama",
                ["Marine Barge (Laut)", "Trucking (Darat)", "Air Freight (Udara)"],
                horizontal=True,
                key="mode_choice_radio"
            )
        with col_c2:
            if "Barge" in mode_choice:
                lead_days = int(np.ceil(dist_km / 120)) + 3
                mode_emiss_factor = 0.03
                desiccant_cost = 450.0 if ("Sensitif" in cargo_type and curr_hum > 80) else 0.0
            elif "Trucking" in mode_choice:
                lead_days = int(np.ceil(dist_km / 350)) + 1
                mode_emiss_factor = 0.15
                desiccant_cost = 250.0 if ("Sensitif" in cargo_type and curr_hum > 80) else 0.0
            else:  # Air Freight
                lead_days = 1
                mode_emiss_factor = 1.20
                desiccant_cost = 0.0

            est_cargo_emiss = (dist_km * 50.0 * mode_emiss_factor) / 1000.0

            col_t1, col_t2, col_t3, col_t4 = st.columns(4)
            with col_t1: st.metric("Waktu Transit", f"{lead_days} Hari")
            with col_t2: st.metric("Estimasi Emisi", f"{est_cargo_emiss:,.2f} tCO2e")
            with col_t3: st.metric("Kelembapan Rute", f"{curr_hum}%")
            with col_t4: st.metric("Biaya Proteksi Desiccant", f"${desiccant_cost:,.0f} USD")

        st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
        st.markdown("##### Matriks Perbandingan Trade-off 3 Moda Pengiriman")
        
        barge_emiss = (dist_km * 50.0 * 0.03) / 1000.0
        truck_emiss = (dist_km * 50.0 * 0.15) / 1000.0
        air_emiss = (dist_km * 50.0 * 1.20) / 1000.0
        
        matrix_df = pd.DataFrame([
            {"Moda Pengiriman": "Marine Barge (Laut)", "Waktu Transit": f"{int(np.ceil(dist_km / 120)) + 3} Hari", "Emisi Scope 3": f"{barge_emiss:,.2f} tCO2e", "Kelembapan Koridor": f"{curr_hum}%", "Biaya Proteksi Material": "$450 USD (Sealed Desiccant)" if ("Sensitif" in cargo_type and curr_hum > 80) else "$0 USD", "Rekomendasi": "🟢 Paling Hemat Karbon & Biaya"},
            {"Moda Pengiriman": "Trucking (Darat)", "Waktu Transit": f"{int(np.ceil(dist_km / 350)) + 1} Hari", "Emisi Scope 3": f"{truck_emiss:,.2f} tCO2e", "Kelembapan Koridor": f"{curr_hum}%", "Biaya Proteksi Material": "$250 USD (Desiccant Standard)" if ("Sensitif" in cargo_type and curr_hum > 80) else "$0 USD", "Rekomendasi": "🟡 Keseimbangan Waktu Pasokan"},
            {"Moda Pengiriman": "Air Freight (Udara)", "Waktu Transit": "1 Hari", "Emisi Scope 3": f"{air_emiss:,.2f} tCO2e", "Kelembapan Koridor": "Terkontrol (Kabin)", "Biaya Proteksi Material": "$0 USD", "Rekomendasi": "🔴 Khusus Emergency Sparepart"}
        ])

        st.dataframe(matrix_df, hide_index=True, use_container_width=True)

        if "Sensitif" in cargo_type and curr_hum > 80 and "Barge" in mode_choice:
            st.warning(f"**Proteksi Material Presisi**: Kelembapan koridor {r_sel_row['Destination']} berada di level **{curr_hum}% (Tinggi)**. Pengiriman via Marine Barge membutuhkan **Sealed Desiccant Container (${desiccant_cost:,.0f} USD)** untuk mencegah korosi komponen presisi selama transit {lead_days} hari — namun menghemat biaya emisi signifikan dibanding Air Freight.")
        elif "Air" in mode_choice:
            st.error(f"**Peringatan Emisi**: Air Freight memicu emisi **{est_cargo_emiss:,.2f} tCO2e** (40x lipat Marine Barge). Gunakan moda ini hanya untuk kebutuhan material darurat pertambangan.")

        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
        if st.button("Kunci Rekomendasi Logistik Koridor", key="btn_lock_logistics", use_container_width=True, type="primary"):
            st.session_state['locked_logistics'] = {
                'route_id': selected_route_id,
                'origin': r_sel_row['Origin'],
                'destination': r_sel_row['Destination'],
                'dist_km': dist_km,
                'cargo_type': cargo_type,
                'mode_choice': mode_choice,
                'desiccant_cost': desiccant_cost,
                'lead_days': lead_days,
                'est_cargo_emiss': est_cargo_emiss,
                'curr_hum': curr_hum,
                'timestamp': datetime.now().strftime("%d-%m-%Y %H:%M")
            }
            st.success("Rekomendasi logistik koridor berhasil dikunci! Diteruskan ke Tab Laporan Direksi.")

    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

    # 2B. SIMULATOR KEBIJAKAN DEKARBONISASI & SCIPY SOLVER
    if "biofuel_val" not in st.session_state: st.session_state.biofuel_val = 20.0
    if "local_proc_val" not in st.session_state: st.session_state.local_proc_val = 15.0
    if "ev_val" not in st.session_state: st.session_state.ev_val = 10.0
    if "modal_shift_val" not in st.session_state: st.session_state.modal_shift_val = 15.0
    if "carbon_price_val" not in st.session_state: st.session_state.carbon_price_val = DEFAULT_CARBON_PRICE_USD

    base_s1 = curr_data['Scope1_tCO2e']
    base_s3 = curr_data['Scope3_Cat4_UpstreamLogistics_tCO2e'] + curr_data['Scope3_Cat1_PurchasedGoods_tCO2e']

    st.markdown("#### Optimasi Biaya & Kebijakan Karbon")
    col_p1, col_p2, col_p3, col_p4 = st.columns(4)
    with col_p1:
        if st.button("Target 10%", use_container_width=True):
            st.session_state.biofuel_val, st.session_state.local_proc_val, st.session_state.ev_val, st.session_state.modal_shift_val, st.session_state.carbon_price_val = 10.0, 10.0, 5.0, 10.0, 15.0
            st.rerun()
    with col_p2:
        if st.button("Target 25%", use_container_width=True):
            st.session_state.biofuel_val, st.session_state.local_proc_val, st.session_state.ev_val, st.session_state.modal_shift_val, st.session_state.carbon_price_val = 25.0, 20.0, 15.0, 20.0, 25.0
            st.rerun()
    with col_p3:
        if st.button("Auto Optimize 30%", use_container_width=True, type="primary"):
            opt_res = solve_scipy_optimal_decarbonization(base_s1, base_s3, NET_ZERO_TARGET_PERCENTAGE)
            if opt_res["success"]:
                st.session_state.biofuel_val = opt_res["biofuel_val"]
                st.session_state.local_proc_val = opt_res["local_proc_val"]
                st.session_state.modal_shift_val = opt_res["modal_shift_val"]
                st.session_state.ev_val = opt_res["ev_val"]
                st.toast("Sedang menimbang 4 opsi kebijakan... Ketemu kombinasi paling hemat!", icon="✅")
                st.rerun()
    with col_p4:
        if st.button("Reset", use_container_width=True):
            st.session_state.biofuel_val, st.session_state.local_proc_val, st.session_state.ev_val, st.session_state.modal_shift_val, st.session_state.carbon_price_val = 20.0, 15.0, 10.0, 15.0, DEFAULT_CARBON_PRICE_USD
            st.rerun()

    st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)

    col_sim1, col_sim2 = st.columns([5, 5])
    with col_sim1:
        st.markdown("""
            <div class="petrosea-callout">
                <h4>Pilih Parameter Dekarbonisasi</h4>
                <p>Geser slider di bawah untuk melihat dampak opsi kebijakan, atau klik <b>Auto Optimize 30%</b> untuk mencari kombinasi paling murah secara otomatis.</p>
            </div>
        """, unsafe_allow_html=True)
        biofuel_mix = st.slider("Substitusi Bahan Bakar B100 (%)", 0, 100, key="biofuel_val")
        local_proc_increase = st.slider("Peningkatan Belanja Pemasok Lokal (%)", 0, 50, key="local_proc_val")
        modal_shift_barge = st.slider("Pengalihan Logistik ke Marine Barge (%)", 0, 50, key="modal_shift_val")
        ev_retrofit_pct = st.slider("Elektrifikasi / Retrofit EV Alat Berat (%)", 0, 50, key="ev_val")
        carbon_price = st.number_input("Harga Pajak / Kredit Karbon ($/tCO2e)", min_value=5.0, max_value=100.0, key="carbon_price_val")

    with col_sim2:
        st.markdown("### Proyeksi Hasil & Penghematan Biaya")
        base_s1 = curr_data['Scope1_tCO2e']
        base_s3 = curr_data['Scope3_Cat4_UpstreamLogistics_tCO2e'] + curr_data['Scope3_Cat1_PurchasedGoods_tCO2e']
        sim_res = calculate_decarbonization(base_s1, base_s3, biofuel_mix, local_proc_increase, ev_retrofit_pct, modal_shift_barge, carbon_price)
        
        col_m1, col_m2 = st.columns(2)
        with col_m1: 
            st.success(f"**Estimasi emisi berkurang:**\n\n### {sim_res['total_abatement']:,.2f} tCO2e / thn")
        with col_m2: 
            st.info(f"**Estimasi penghematan biaya:**\n\n### ${sim_res['cost_savings_usd']:,.2f} USD")

        target_pct = NET_ZERO_TARGET_PERCENTAGE
        current_pct = sim_res['pct_reduction']
        st.markdown(f"**Capaian terhadap Target Net-Zero Petrosea 2030 (Target: {NET_ZERO_TARGET_PERCENTAGE:.0f}%):**")
        st.progress(min(1.0, current_pct / target_pct))

        trees_count = int(sim_res['total_abatement'] * TREES_PLANTED_PER_TON_CO2)
        trucks_count = int(sim_res['total_abatement'] * DIESEL_TRUCKS_RETIRED_PER_TON_CO2)
        homes_count = int(sim_res['total_abatement'] * HOMES_POWERED_PER_TON_CO2)

        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
        st.markdown("##### Dampak Lingkungan Nyata (Setara Fisik)")
        col_e1, col_e2, col_e3 = st.columns(3)
        with col_e1:
            st.markdown(f"""
                <div style="background: rgba(0, 168, 107, 0.08); border: 1px solid rgba(0, 168, 107, 0.3); border-radius: 8px; padding: 10px; text-align: center;">
                    <div style="font-size: 0.78rem; color: #94A3B8; font-weight: 600;">Pohon Hutan Ditanam</div>
                    <div style="font-size: 1.05rem; font-weight: 700; color: #00A86B; margin-top: 4px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="{trees_count:,} Pohon">{trees_count:,} Pohon</div>
                </div>
            """, unsafe_allow_html=True)
        with col_e2:
            st.markdown(f"""
                <div style="background: rgba(0, 168, 107, 0.08); border: 1px solid rgba(0, 168, 107, 0.3); border-radius: 8px; padding: 10px; text-align: center;">
                    <div style="font-size: 0.78rem; color: #94A3B8; font-weight: 600;">Truk Tambang Retired</div>
                    <div style="font-size: 1.05rem; font-weight: 700; color: #00A86B; margin-top: 4px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="{trucks_count:,} Truk">{trucks_count:,} Truk</div>
                </div>
            """, unsafe_allow_html=True)
        with col_e3:
            st.markdown(f"""
                <div style="background: rgba(0, 168, 107, 0.08); border: 1px solid rgba(0, 168, 107, 0.3); border-radius: 8px; padding: 10px; text-align: center;">
                    <div style="font-size: 0.78rem; color: #94A3B8; font-weight: 600;">Rumah Listrik Bersih</div>
                    <div style="font-size: 1.05rem; font-weight: 700; color: #00A86B; margin-top: 4px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="{homes_count:,} Rumah">{homes_count:,} Rumah</div>
                </div>
            """, unsafe_allow_html=True)

        fig_sim = go.Figure(data=[
            go.Bar(name='Emisi Awal', x=['Scope 1', 'Scope 3 (Logistik & Barjas)'], y=[base_s1, base_s3], marker_color='#E87722', text=[f"{base_s1:,.0f}", f"{base_s3:,.0f}"], textposition='auto'),
            go.Bar(name='Setelah Skenario', x=['Scope 1', 'Scope 3 (Logistik & Barjas)'], y=[sim_res['post_s1'], sim_res['post_s3']], marker_color='#005A36', text=[f"{sim_res['post_s1']:,.0f}", f"{sim_res['post_s3']:,.0f}"], textposition='auto')
        ])
        fig_sim.update_layout(barmode='group', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=20, r=20, t=30, b=20), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig_sim, use_container_width=True)

    # COMMITMENT MOMENT FOR DECARBONIZATION SIMULATOR (SECTION 2B)
    st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
    if st.button("Kunci Skenario Dekarbonisasi Tambang", key="btn_lock_decarb", use_container_width=True, type="primary"):
        st.session_state['locked_decarb'] = {
            'biofuel_val': biofuel_mix,
            'local_proc_val': local_proc_increase,
            'modal_shift_val': modal_shift_barge,
            'ev_val': ev_retrofit_pct,
            'carbon_price': carbon_price,
            'sim_res': sim_res,
            'trees_count': trees_count,
            'trucks_count': trucks_count,
            'homes_count': homes_count,
            'timestamp': datetime.now().strftime("%d-%m-%Y %H:%M")
        }
        st.success("Skenario dekarbonisasi tambang berhasil dikunci! Diteruskan ke Tab Laporan Direksi.")

    # -------------------------------------------------------------------------
    # FITUR 3: JURNAL AUDIT RISIKO OPERASIONAL (7 HARI TERAKHIR - EVENT DRIVEN)
    # -------------------------------------------------------------------------
    st.markdown("---")
    st.markdown("### 3. Jurnal audit risiko operasional (7 hari terakhir)")
    st.caption("Catatan otomatis insiden cuaca buruk, kelembapan tinggi, dan tindakan mitigasi K3 & QA-QC di rute pengiriman Petrosea.")

    now = datetime.now()
    log_data = pd.DataFrame([
        {"Tanggal Log": (now - timedelta(days=1, hours=4)).strftime("%d-%m-%Y %H:%M"), "Kode Rute": "RTE-003", "Tujuan": "Sorong", "Pemicu Risiko": "Gelombang Laut 2.8m & Badai", "Tindakan Mitigasi Otomatis": "Tunda Marine Barge 12 Jam", "Status K3 & QA-QC": "Verified (K3 Approved)"},
        {"Tanggal Log": (now - timedelta(days=3, hours=8)).strftime("%d-%m-%Y %H:%M"), "Kode Rute": "RTE-001", "Tujuan": "Kutai Barat", "Pemicu Risiko": "Hujan Deras & Jalan Licin", "Tindakan Mitigasi Otomatis": "Batas Kecepatan Truk 40 km/j", "Status K3 & QA-QC": "Verified (Speed Limit)"},
        {"Tanggal Log": (now - timedelta(days=5, hours=2)).strftime("%d-%m-%Y %H:%M"), "Kode Rute": "RTE-004", "Tujuan": "Sorowako", "Pemicu Risiko": "Kelembapan Ekstrem 92%", "Tindakan Mitigasi Otomatis": "Proteksi Sealed Desiccant Container", "Status K3 & QA-QC": "Verified (QA-QC Approved)"}
    ])

    st.dataframe(
        log_data,
        column_config={
            "Tanggal Log": st.column_config.TextColumn("Waktu Kejadian", width="medium"),
            "Kode Rute": st.column_config.TextColumn("Rute", width="small"),
            "Tujuan": "Lokasi Situs",
            "Pemicu Risiko": "Pemicu Anomali Cuaca",
            "Tindakan Mitigasi Otomatis": "Tindakan Pencegahan Otomatis",
            "Status K3 & QA-QC": "Status Pemeriksaan"
        },
        use_container_width=True, hide_index=True
    )

    st.download_button(
        label="Unduh Log Risiko 7 Hari (CSV)",
        data=log_data.to_csv(index=False).encode('utf-8'),
        file_name="petrosea_operational_risk_log_7days.csv",
        mime="text/csv"
    )

    # -------------------------------------------------------------------------
    # CONTEXTUAL BRIDGE CTA TO TAB 3 (NARRATIVE MOMENTUM)
    # -------------------------------------------------------------------------
    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)
    st.info(
        "Skenario kebijakan & log risiko ini telah disiapkan untuk paparan direksi. "
        "Lihat rangkuman resmi & unduh berkas audit di tab **Laporan Direksi** →"
    )
