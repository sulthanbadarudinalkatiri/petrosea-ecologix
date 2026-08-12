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
import concurrent.futures

try:
    from streamlit_folium import st_folium
    HAS_ST_FOLIUM = True
except ImportError:
    HAS_ST_FOLIUM = False

from modules.constants import (
    ASSUMPTION_REGISTRY,
    BIOFUEL_B100_ABATEMENT_FACTOR,
    EV_RETROFIT_ABATEMENT_FACTOR,
    LOCAL_PROC_LOGISTICS_ABATEMENT_FACTOR,
    BARGE_INTERMODAL_SHIFT_ABATEMENT_FACTOR,
    NET_ZERO_TARGET_PERCENTAGE,
    DEFAULT_CARBON_PRICE_USD,
    TREES_PLANTED_PER_TON_CO2,
    DIESEL_TRUCKS_RETIRED_PER_TON_CO2,
    HOMES_POWERED_PER_TON_CO2,
    EMISSION_FACTOR_BARGE_KG_PER_TKM,
    EMISSION_FACTOR_TRUCK_KG_PER_TKM,
    EMISSION_FACTOR_AIR_KG_PER_TKM,
    MC_BIOFUEL_USD_PER_TCO2E,
    MC_LOCAL_PROCUREMENT_USD_PER_TCO2E,
    MC_BARGE_MODAL_SHIFT_USD_PER_TCO2E,
    MC_EV_RETROFIT_USD_PER_TCO2E,
    DEFAULT_PAYLOAD_TRUCK,
    DEFAULT_PAYLOAD_BARGE,
    DEFAULT_PAYLOAD_VESSEL,
    BARGE_SPEED_KM_PER_DAY,
    TRUCK_SPEED_KM_PER_DAY,
    BARGE_LOADING_BUFFER_DAYS,
    TRUCK_LOADING_BUFFER_DAYS,
    DESICCANT_COST_BARGE_USD,
    DESICCANT_COST_TRUCK_USD,
    HUMIDITY_THRESHOLD_DESICCANT_PCT,
    MAX_BIOFUEL_MIX,
    MAX_LOCAL_PROCUREMENT,
    MAX_BARGE_MODAL_SHIFT,
    MAX_EV_RETROFIT,
    BIOFUEL_OVERLAP_FACTOR,
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
            "status": "OK",
            "temp": float(curr.get("temperature", 28.5)),
            "kec_angin": float(curr.get("windspeed", 12.0)),
            "arah_angin": f"{float(curr.get('winddirection', 180))}°",
            "cuaca": cuaca_text,
            "kelembapan": float(curr_humidity),
            "lokasi_lengkap": f"Koordinat {lat:.2f}, {lon:.2f}"
        }
    except Exception:
        return {
            "status": "ERROR",
            "temp": None,
            "kec_angin": None,
            "arah_angin": None,
            "cuaca": "Weather unavailable",
            "kelembapan": None,
            "lokasi_lengkap": f"Koordinat {lat:.2f}, {lon:.2f} (Source status: ERROR)"
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

@st.cache_data(ttl=3600)
def fetch_hourly_telemetry(lat: float, lon: float, mode: str = "historical") -> pd.DataFrame:
    """
    Fetch 168 hours of hourly weather telemetry data from Open-Meteo API.
    mode: 'historical' (past 7 days = 168 hours) or 'forecast' (next 7 days = 168 hours)
    """
    try:
        if mode == "historical":
            url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&past_days=7&forecast_days=1&hourly=temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,weather_code&timezone=auto"
        else:
            url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&forecast_days=7&hourly=temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,weather_code&timezone=auto"
        
        res = requests.get(url, timeout=4).json()
        h = res.get("hourly", {})
        df = pd.DataFrame({
            "time": h.get("time", []),
            "temp": h.get("temperature_2m", []),
            "hum": h.get("relative_humidity_2m", []),
            "precip": h.get("precipitation", []),
            "wind": h.get("wind_speed_10m", []),
            "code": h.get("weather_code", [])
        })

        if mode == "historical" and not df.empty:
            df['time_dt'] = pd.to_datetime(df['time'])
            df = df[df['time_dt'] <= datetime.now()].copy()
            # Enforce exactly 168 hours (7 days) retrospectively
            df = df.tail(168)
            df.drop(columns=['time_dt'], inplace=True)

        return df
    except Exception:
        return pd.DataFrame()

def reconstruct_event_journal(df_h: pd.DataFrame, route_id: str, dest: str) -> pd.DataFrame:
    """
    Filters and deduplicates 168 hourly observations into meaningful operational events.
    Applies Severity Rules (Advisory, Warning, Critical) & Compound Risk Detection.
    Merges consecutive hourly triggers into single Event Windows with authentic timestamps.
    """
    if df_h.empty:
        return pd.DataFrame()

    events = []
    current_event = None

    for idx, row in df_h.iterrows():
        try:
            # Gunakan pd.to_datetime untuk parser yang jauh lebih tangguh terhadap variasi format API
            t_dt = pd.to_datetime(row['time']).to_pydatetime()
            
            # Safe casting: handles None, "", or malformed strings gracefully
            wind_raw = row.get('wind')
            w = float(wind_raw) if wind_raw not in (None, "") else 0.0
            
            precip_raw = row.get('precip')
            p = float(precip_raw) if precip_raw not in (None, "") else 0.0
            
            hum_raw = row.get('hum')
            h = float(hum_raw) if hum_raw not in (None, "") else 75.0
            
        except (ValueError, TypeError, Exception):
            continue

        has_wind = w >= 25.0
        has_rain = p >= 1.0
        has_hum = h >= 85.0

        if not (has_wind or has_rain or has_hum):
            if current_event:
                events.append(current_event)
                current_event = None
            continue

        # Severity & Compound Risk Classification
        if has_wind and has_rain:
            severity = "🔴 Critical (Compound Risk)"
            category = "COMPOUND RISK: High Wind & Heavy Rain"
            risk_desc = f"Angin Kencang ({w:.1f} km/j) + Hujan Deras ({p:.1f} mm/jam)"
            action = "Tunda Keberangkatan Marine Barge & Penambatan Armada"
            rank = 4
        elif has_wind:
            severity = "🟡 Warning"
            category = "SUSTAINED HIGH WIND"
            risk_desc = f"Kecepatan Angin Kencang {w:.1f} km/j"
            action = "Pengawasan Stabilitas Tugboat & Evaluasi Operasi Laut"
            rank = 3
        elif has_rain:
            severity = "🟡 Warning"
            category = "HEAVY PRECIPITATION"
            risk_desc = f"Curah Hujan Tinggi {p:.1f} mm/jam"
            action = "Pembatasan Kecepatan Truk 30 km/j & Evaluasi Drainage Situs"
            rank = 2
        else:
            severity = "🟢 Advisory"
            category = "HIGH HUMIDITY ENVIRONMENT"
            risk_desc = f"Kelembapan Udara Ekstrem {h:.0f}%"
            action = "Proteksi Sealed Desiccant Container Wajib"
            rank = 1

        if current_event is None:
            current_event = {
                'route_id': route_id,
                'dest': dest,
                'start_dt': t_dt,
                'end_dt': t_dt,
                'category': category,
                'severity': severity,
                'risk_desc': risk_desc,
                'action': action,
                'hours_count': 1,
                'rank': rank
            }
        else:
            time_diff = (t_dt - current_event['end_dt']).total_seconds() / 3600.0
            
            # Jendela Toleransi 2 Jam (Micro-Fluctuation Fix) & Eskalasi (Evolution Fix)
            if time_diff <= 2.0 and current_event['route_id'] == route_id:
                current_event['end_dt'] = t_dt
                current_event['hours_count'] += int(time_diff)
                
                # Jika event yang baru lebih parah, eskalasi status keseluruhan window
                if rank > current_event.get('rank', 0):
                    current_event['category'] = category
                    current_event['severity'] = severity
                    current_event['risk_desc'] = risk_desc
                    current_event['action'] = action
                    current_event['rank'] = rank
            else:
                events.append(current_event)
                current_event = {
                    'route_id': route_id,
                    'dest': dest,
                    'start_dt': t_dt,
                    'end_dt': t_dt,
                    'category': category,
                    'severity': severity,
                    'risk_desc': risk_desc,
                    'action': action,
                    'hours_count': 1,
                    'rank': rank
                }

    if current_event:
        events.append(current_event)

    formatted_rows = []
    for e in events:
        start_str = e['start_dt'].strftime('%d %b %H:%M')
        # Correctly add 1 hour to the end timestamp to represent the full duration block
        actual_end_dt = e['end_dt'] + timedelta(hours=1)
        end_str = actual_end_dt.strftime('%H:%M')
        
        duration_str = f"{e['hours_count']} Jam" if e['hours_count'] > 1 else "1 Jam"
        window_str = f"{start_str} – {end_str} ({duration_str})"

        formatted_rows.append({
            "Rentang Waktu (Telemetri)": window_str,
            "Rute / Situs": f"{e['route_id']} ({e['dest']})",
            "Kategori Event Risiko": e['category'],
            "Tingkat Keparahan": e['severity'],
            "Indikator Telemetri": e['risk_desc'],
            "Tindakan Mitigasi K3": e['action']
        })

    return pd.DataFrame(formatted_rows)

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
    carbon_price: float = DEFAULT_CARBON_PRICE_USD,
    dist_km: float = 100.0,
    payload: float = 50.0
) -> Dict[str, float]:
    reduction_s1_ev = base_s1 * (ev_retrofit_pct / 100.0) * EV_RETROFIT_ABATEMENT_FACTOR
    remaining_s1_diesel = max(0.0, base_s1 - reduction_s1_ev)
    reduction_s1_biofuel = remaining_s1_diesel * (biofuel_mix / 100.0) * BIOFUEL_B100_ABATEMENT_FACTOR
    total_s1_reduction = reduction_s1_ev + reduction_s1_biofuel
    post_s1 = max(0.0, base_s1 - total_s1_reduction)

    reduction_s3_barge = base_s3 * (modal_shift_barge / 100.0) * BARGE_INTERMODAL_SHIFT_ABATEMENT_FACTOR
    remaining_s3_logistics = max(0.0, base_s3 - reduction_s3_barge)
    reduction_s3_local = remaining_s3_logistics * (local_proc_increase / 100.0) * LOCAL_PROC_LOGISTICS_ABATEMENT_FACTOR
    total_s3_reduction = reduction_s3_local + reduction_s3_barge
    post_s3 = max(0.0, base_s3 - total_s3_reduction)

    total_abatement = total_s1_reduction + total_s3_reduction
    pct_reduction = (total_abatement / (base_s1 + base_s3)) * 100.0 if (base_s1 + base_s3) > 0 else 0.0

    mc_biofuel = MC_BIOFUEL_USD_PER_TCO2E
    mc_ev = MC_EV_RETROFIT_USD_PER_TCO2E
    # Dynamic MAC Scaling: Local procurement savings scale with distance.
    mc_local = MC_LOCAL_PROCUREMENT_USD_PER_TCO2E * (dist_km / 350.0)
    # Barge savings scale with distance and payload economy of scale.
    mc_barge = MC_BARGE_MODAL_SHIFT_USD_PER_TCO2E * (dist_km / 120.0) * (payload / 500.0)

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
    carbon_price: float = DEFAULT_CARBON_PRICE_USD,
    dist_km: float = 100.0,
    payload: float = 50.0
) -> Dict[str, Any]:
    total_baseline = base_s1 + base_s3
    required_abatement = total_baseline * (target_pct / 100.0)

    abate_biofuel_per_pct = base_s1 * (1.0 - BIOFUEL_OVERLAP_FACTOR * EV_RETROFIT_ABATEMENT_FACTOR) * 0.01 * BIOFUEL_B100_ABATEMENT_FACTOR
    abate_local_per_pct = base_s3 * 0.01 * LOCAL_PROC_LOGISTICS_ABATEMENT_FACTOR
    abate_barge_per_pct = base_s3 * 0.01 * BARGE_INTERMODAL_SHIFT_ABATEMENT_FACTOR
    abate_ev_per_pct = base_s1 * 0.01 * EV_RETROFIT_ABATEMENT_FACTOR

    mc_biofuel = MC_BIOFUEL_USD_PER_TCO2E
    mc_ev = MC_EV_RETROFIT_USD_PER_TCO2E
    # Dynamic MAC Scaling
    mc_local = MC_LOCAL_PROCUREMENT_USD_PER_TCO2E * (dist_km / 350.0)
    mc_barge = MC_BARGE_MODAL_SHIFT_USD_PER_TCO2E * (dist_km / 120.0) * (payload / 500.0)

    c = [
        abate_biofuel_per_pct * (mc_biofuel - carbon_price),
        abate_local_per_pct * (mc_local - carbon_price),
        abate_barge_per_pct * (mc_barge - carbon_price),
        abate_ev_per_pct * (mc_ev - carbon_price)
    ]

    A_ub = [
        [-abate_biofuel_per_pct, -abate_local_per_pct, -abate_barge_per_pct, -abate_ev_per_pct],
        [abate_biofuel_per_pct, 0, 0, abate_ev_per_pct],
        [0, abate_local_per_pct, abate_barge_per_pct, 0]
    ]
    b_ub = [-required_abatement, base_s1, base_s3]

    bounds = [(0, MAX_BIOFUEL_MIX), (0, MAX_LOCAL_PROCUREMENT), (0, MAX_BARGE_MODAL_SHIFT), (0, MAX_EV_RETROFIT)]

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
            "biofuel_val": 0.0, "local_proc_val": 0.0,
            "modal_shift_val": 0.0, "ev_val": 0.0,
            "opt_cost_usd": 0.0
        }

# -----------------------------------------------------------------------------
# MAIN RENDER FUNCTION FOR TAB 2
# -----------------------------------------------------------------------------
def render_tab2_optimizer(df_routes: pd.DataFrame, curr_data: pd.Series):
    """
    Renders Tab 2: Simulator Logistik & 3 Fitur Unggulan Operasional.
    Follows a strict 1 -> 2 -> 3 downward narrative flow.
    """
    st.subheader("Simulator Logistik")
    st.caption("Peta cuaca, log risiko pengiriman, dan kalkulator emisi.")
    st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # FITUR 1: Kondisi Cuaca Koridor Pengiriman
    # -------------------------------------------------------------------------
    st.markdown("### 1. Kondisi Cuaca Koridor Pengiriman")
    st.caption("Cek kondisi cuaca dan kualitas udara real-time di tiap koridor pengiriman buat antisipasi delay operasional.")

    weather_cache = {}
    aqi_cache = {}
    bad_weather_sites = []
    table_rows = []

    def _fetch_both(row):
        return (
            row['Route_ID'],
            fetch_weather_data(row['Lat_Dest'], row['Lon_Dest']),
            fetch_aqi_data(row['Lat_Dest'], row['Lon_Dest'])
        )

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_row = {executor.submit(_fetch_both, row): row for idx, row in df_routes.iterrows()}
        
        try:
            for future in concurrent.futures.as_completed(future_to_row, timeout=10.0):
                try:
                    route_id, w_info, a_info = future.result()
                    weather_cache[route_id] = w_info
                    aqi_cache[route_id] = a_info
                except Exception as exc:
                    row = future_to_row[future]
                    weather_cache[row['Route_ID']] = {"status": "ERROR", "cuaca": "Error", "temp": 0, "kelembapan": 0}
                    aqi_cache[row['Route_ID']] = {"status": "ERROR", "aqi": 0}
        except concurrent.futures.TimeoutError:
            st.warning("⚠️ Peringatan: API Cuaca eksternal mengalami timeout. Sebagian data cuaca rute menggunakan *fallback*.")
            # Berikan nilai default untuk future yang belum selesai
            for future, row in future_to_row.items():
                if row['Route_ID'] not in weather_cache:
                    weather_cache[row['Route_ID']] = {"status": "ERROR", "cuaca": "Timeout", "temp": 0, "kelembapan": 0}
                    aqi_cache[row['Route_ID']] = {"status": "ERROR", "aqi": 0}

    for idx, row in df_routes.iterrows():
        w_info = weather_cache[row['Route_ID']]
        a_info = aqi_cache[row['Route_ID']]
        cuaca_text = w_info['cuaca']
        
        if w_info.get("status") == "ERROR":
            status_risk, action_rec = "Data Tidak Tersedia (API Error)", "Gunakan Prosedur Standar"
            cuaca_text = "Weather unavailable"
        elif any(w in cuaca_text for w in ["Hujan", "Petir", "Deras", "Badai"]):
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
            "Cuaca Real-Time": f"{cuaca_text}" if w_info.get("status") == "ERROR" else f"{cuaca_text} ({w_info['temp']}°C)",
            "Kelembapan": "N/A" if w_info.get("status") == "ERROR" else f"{w_info['kelembapan']}%",
            "Kualitas Udara": f"AQI {a_info['aqi']}",
            "Status Risiko": status_risk,
            "Rekomendasi Operasional": action_rec
        })

    if bad_weather_sites:
        st.error(f"⚠️ Cuaca buruk di **{', '.join(bad_weather_sites)}**. Pengiriman via laut di rute ini sebaiknya ditunda.")
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
    # FITUR 2: JURNAL AUDIT RISIKO OPERASIONAL & WEATHER INTELLIGENCE RECONSTRUCTION
    # -------------------------------------------------------------------------
    st.markdown("---")
    st.markdown("### 2. Radar K3: Deteksi Ancaman & Mitigasi Risiko Cuaca")
    st.caption("Sistem memantau kondisi operasional secara real-time. Jika ditemukan pola yang berisiko, sistem akan segera memberi tahu tim K3 agar langkah antisipasi bisa langsung diambil.")

    horizon_col1, horizon_col2 = st.columns([6, 4])
    with horizon_col1:
        time_horizon = st.radio(
            "Pilih rentang waktu data:",
            options=["7 Hari Terakhir", "Prakiraan 7 Hari Ke Depan"],
            index=1,
            horizontal=True,
            key="horizon_mode_selector"
        )

    mode_key = "historical" if "Terakhir" in time_horizon else "forecast"
    all_events_list = []
    total_raw_obs = 0

    for idx, row in df_routes.iterrows():
        r_id = row['Route_ID']
        dest = row['Destination']
        lat = row['Lat_Dest']
        lon = row['Lon_Dest']
        
        df_h = fetch_hourly_telemetry(lat, lon, mode=mode_key)
        if not df_h.empty:
            total_raw_obs += len(df_h)
            df_ev = reconstruct_event_journal(df_h, r_id, dest)
            if not df_ev.empty:
                all_events_list.append(df_ev)

    if all_events_list:
        combined_events = pd.concat(all_events_list, ignore_index=True)
    else:
        combined_events = pd.DataFrame(columns=[
            "Rentang Waktu (Telemetri)", "Rute / Situs", "Kategori Event Risiko",
            "Tingkat Keparahan", "Indikator Telemetri", "Tindakan Mitigasi K3"
        ])

    total_obs = total_raw_obs
    total_events = len(combined_events)
    critical_cnt = len(combined_events[combined_events['Tingkat Keparahan'].str.contains('Critical', case=False)]) if not combined_events.empty else 0
    warning_cnt = len(combined_events[combined_events['Tingkat Keparahan'].str.contains('Warning', case=False)]) if not combined_events.empty else 0
    advisory_cnt = len(combined_events[combined_events['Tingkat Keparahan'].str.contains('Advisory', case=False)]) if not combined_events.empty else 0

    # Executive Telemetry Filtering Summary Container (Clean UI/UX)
    st.markdown(f"""
        <div style="padding: 16px; background-color: var(--secondary-background-color); border: 1px solid var(--faded-text-color); border-radius: 8px; margin-bottom: 24px;">
            <div style="font-size: 0.92rem; color: var(--text-color); opacity: 0.9; margin-bottom: 12px; line-height: 1.5;">Dari <b>{total_obs}</b> titik data, sistem menyaring yang keluar dari ambang batas aman:</div>
            <div style="display: flex; gap: 12px; align-items: center; font-size: 0.9rem; font-weight: 600; margin-bottom: 10px;">
                <span style="background-color: rgba(235, 87, 87, 0.15); color: #FF4D4D; padding: 4px 10px; border-radius: 4px; border: 1px solid rgba(255,77,77,0.3);">🔴 {critical_cnt} Critical</span>
                <span style="background-color: rgba(242, 201, 76, 0.15); color: #F2C94C; padding: 4px 10px; border-radius: 4px; border: 1px solid rgba(242,201,76,0.3);">🟡 {warning_cnt} Warning</span>
                <span style="background-color: rgba(39, 174, 96, 0.15); color: #27AE60; padding: 4px 10px; border-radius: 4px; border: 1px solid rgba(39,174,96,0.3);">🟢 {advisory_cnt} Advisory</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    with st.expander("🔍 Lihat Rincian Jurnal Log Cuaca", expanded=False):
        if not combined_events.empty:
            st.dataframe(
                combined_events,
                column_config={
                    "Rentang Waktu (Telemetri)": st.column_config.TextColumn("Rentang Waktu Event Window", width="medium"),
                    "Rute / Situs": st.column_config.TextColumn("Koridor Situs", width="small"),
                    "Kategori Event Risiko": st.column_config.TextColumn("Klasifikasi Event", width="medium"),
                    "Tingkat Keparahan": st.column_config.TextColumn("Severity Level", width="small"),
                    "Indikator Telemetri": "Indikator Telemetri Open-Meteo",
                    "Tindakan Mitigasi K3": "Rekomendasi Respons Mitigasi K3"
                },
                use_container_width=True, hide_index=True
            )
        else:
            st.success("Seluruh 840 titik observasi telemetri dalam batas aman normal (No Operational Risk Events Detected).")

        # Clean CSV Export Formatting
        csv_export_df = combined_events.rename(columns={
            "Rentang Waktu (Telemetri)": "Rentang_Waktu_Telemetri",
            "Rute / Situs": "Kode_Rute_dan_Situs",
            "Kategori Event Risiko": "Kategori_Event_Risiko",
            "Tingkat Keparahan": "Tingkat_Keparahan",
            "Indikator Telemetri": "Indikator_Telemetri",
            "Tindakan Mitigasi K3": "Tindakan_Mitigasi_K3"
        })

        st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)
        st.download_button(
            label="Unduh Rekonstruksi Log Risiko Operasional (CSV)",
            data=csv_export_df.to_csv(index=False).encode('utf-8'),
            file_name=f"petrosea_operational_risk_event_journal_{mode_key}.csv",
            mime="text/csv"
        )

        st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)


    # -------------------------------------------------------------------------
    # FITUR 3: OPTIMASI RUTE INTERMODAL & SIMULASI KEBIJAKAN KARBON (TENGAH)
    # -------------------------------------------------------------------------
    st.markdown("---")
    st.markdown("### 3. Simulasi Biaya & Emisi antar Moda Pengiriman")
    st.caption("Hitung trade-off waktu tempuh, biaya logistik, dan dampak karbon sebelum armada bergerak.")

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
                lead_days = int(np.ceil(dist_km / BARGE_SPEED_KM_PER_DAY)) + BARGE_LOADING_BUFFER_DAYS
                mode_emiss_factor = EMISSION_FACTOR_BARGE_KG_PER_TKM
                payload = r_sel_row['Avg_Payload_Tons'] if r_sel_row['Avg_Payload_Tons'] > 0 else DEFAULT_PAYLOAD_BARGE
                # Cost is dynamically calculated per payload volume instead of flat rate
                desiccant_cost = DESICCANT_COST_BARGE_USD * (payload / 500.0) if ("Sensitif" in cargo_type and curr_hum > HUMIDITY_THRESHOLD_DESICCANT_PCT) else 0.0
            elif "Trucking" in mode_choice:
                lead_days = int(np.ceil(dist_km / TRUCK_SPEED_KM_PER_DAY)) + TRUCK_LOADING_BUFFER_DAYS
                mode_emiss_factor = EMISSION_FACTOR_TRUCK_KG_PER_TKM
                payload = r_sel_row['Avg_Payload_Tons'] if r_sel_row['Avg_Payload_Tons'] > 0 else DEFAULT_PAYLOAD_TRUCK
                desiccant_cost = DESICCANT_COST_TRUCK_USD * (payload / 35.0) if ("Sensitif" in cargo_type and curr_hum > HUMIDITY_THRESHOLD_DESICCANT_PCT) else 0.0
            else:  # Air Freight
                lead_days = 1
                mode_emiss_factor = EMISSION_FACTOR_AIR_KG_PER_TKM
                desiccant_cost = 0.0
                payload = r_sel_row['Avg_Payload_Tons'] if r_sel_row['Avg_Payload_Tons'] > 0 else DEFAULT_PAYLOAD_VESSEL

            est_cargo_emiss = (dist_km * payload * mode_emiss_factor) / 1000.0

            col_t1, col_t2, col_t3, col_t4 = st.columns(4)
            with col_t1: st.metric("Waktu Transit", f"{lead_days} Hari")
            with col_t2: st.metric("Estimasi Emisi", f"{est_cargo_emiss:,.2f} tCO2e")
            with col_t3: st.metric("Kelembapan Rute", f"{curr_hum}%")
            with col_t4: st.metric("Biaya Proteksi Desiccant", f"${desiccant_cost:,.0f} USD")

        st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
        st.markdown("##### Matriks Perbandingan Trade-off 3 Moda Pengiriman")
        
        barge_emiss = (dist_km * payload * EMISSION_FACTOR_BARGE_KG_PER_TKM) / 1000.0
        truck_emiss = (dist_km * payload * EMISSION_FACTOR_TRUCK_KG_PER_TKM) / 1000.0
        air_emiss = (dist_km * payload * EMISSION_FACTOR_AIR_KG_PER_TKM) / 1000.0
        
        matrix_df = pd.DataFrame([
            {"Moda Pengiriman": "Marine Barge (Laut)", "Waktu Transit": f"{int(np.ceil(dist_km / BARGE_SPEED_KM_PER_DAY)) + BARGE_LOADING_BUFFER_DAYS} Hari", "Emisi Scope 3": f"{barge_emiss:,.2f} tCO2e", "Kelembapan Koridor": f"{curr_hum}%", "Biaya Proteksi Material": f"${DESICCANT_COST_BARGE_USD:,.0f} USD (Sealed Desiccant)" if ("Sensitif" in cargo_type and curr_hum > HUMIDITY_THRESHOLD_DESICCANT_PCT) else "$0 USD", "Rekomendasi": "🟢 Paling Hemat Karbon & Biaya"},
            {"Moda Pengiriman": "Trucking (Darat)", "Waktu Transit": f"{int(np.ceil(dist_km / TRUCK_SPEED_KM_PER_DAY)) + TRUCK_LOADING_BUFFER_DAYS} Hari", "Emisi Scope 3": f"{truck_emiss:,.2f} tCO2e", "Kelembapan Koridor": f"{curr_hum}%", "Biaya Proteksi Material": f"${DESICCANT_COST_TRUCK_USD:,.0f} USD (Desiccant Standard)" if ("Sensitif" in cargo_type and curr_hum > HUMIDITY_THRESHOLD_DESICCANT_PCT) else "$0 USD", "Rekomendasi": "🟡 Keseimbangan Waktu Pasokan"},
            {"Moda Pengiriman": "Air Freight (Udara)", "Waktu Transit": "1 Hari", "Emisi Scope 3": f"{air_emiss:,.2f} tCO2e", "Kelembapan Koridor": "Terkontrol (Kabin)", "Biaya Proteksi Material": "$0 USD", "Rekomendasi": "🔴 Khusus Emergency Sparepart"}
        ])

        st.dataframe(matrix_df, hide_index=True, use_container_width=True)

        if "Sensitif" in cargo_type and curr_hum > 80 and "Barge" in mode_choice:
            st.warning(f"**Proteksi Material Presisi**: Kelembapan koridor {r_sel_row['Destination']} berada di level **{curr_hum}% (Tinggi)**. Pengiriman via Marine Barge membutuhkan **Sealed Desiccant Container (${desiccant_cost:,.0f} USD)** untuk mencegah korosi komponen presisi selama transit {lead_days} hari — namun menghemat biaya emisi signifikan dibanding Air Freight.")
        elif "Air" in mode_choice:
            st.error(f"Emisi Air Freight (**{est_cargo_emiss:,.2f} tCO2e**) kira-kira 40x lipat dari Barge. Coba pakai opsi ini buat kondisi darurat aja.")


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

    with st.expander("🔎 Lihat Parameter & Asumsi Perhitungan (Assumption Registry)"):
        st.markdown("""
        Setiap parameter numerik yang digunakan dalam perhitungan matriks di atas didokumentasikan di sini
        beserta **sumber referensi**, **tingkat keyakinan**, dan **satuan**. Hal ini memastikan
        transparansi penuh bagi Direksi dan auditor.
        """)

        registry_df = pd.DataFrame(ASSUMPTION_REGISTRY)
        display_df = registry_df[['parameter', 'value', 'unit', 'type', 'evidence_level', 'source', 'category']].copy()
        display_df.columns = ['Parameter', 'Nilai', 'Satuan', 'Type', 'Evidence Level', 'Sumber / Referensi', 'Kategori']

        # Category filter
        categories = sorted(display_df['Kategori'].unique().tolist())
        selected_cats = st.multiselect(
            "Filter berdasarkan kategori:",
            options=categories,
            default=categories,
            key="assumption_cat_filter"
        )
        filtered_df = display_df[display_df['Kategori'].isin(selected_cats)]

        # Confidence summary badges
        high_cnt = len(filtered_df[filtered_df['Evidence Level'] == 'High'])
        med_cnt = len(filtered_df[filtered_df['Evidence Level'] == 'Medium'])
        low_cnt = len(filtered_df[filtered_df['Evidence Level'] == 'Low'])

        st.markdown(f"""
            <div style="display: flex; gap: 10px; margin-bottom: 14px; align-items: center; font-size: 0.88rem; font-weight: 600;">
                <span style="background-color: rgba(39,174,96,0.15); color: #27AE60; padding: 4px 10px; border-radius: 4px; border: 1px solid rgba(39,174,96,0.3);">🟢 {high_cnt} High</span>
                <span style="background-color: rgba(242,201,76,0.15); color: #F2C94C; padding: 4px 10px; border-radius: 4px; border: 1px solid rgba(242,201,76,0.3);">🟡 {med_cnt} Medium</span>
                <span style="background-color: rgba(235,87,87,0.15); color: #FF4D4D; padding: 4px 10px; border-radius: 4px; border: 1px solid rgba(255,77,77,0.3);">🔴 {low_cnt} Low</span>
            </div>
        """, unsafe_allow_html=True)

        st.dataframe(
            filtered_df,
            column_config={
                "Parameter": st.column_config.TextColumn("Parameter", width="medium"),
                "Nilai": st.column_config.NumberColumn("Nilai", format="%.4g"),
                "Satuan": st.column_config.TextColumn("Satuan", width="small"),
                "Type": st.column_config.TextColumn("Type", width="small"),
                "Evidence Level": st.column_config.TextColumn("Evidence Level", width="small"),
                "Sumber / Referensi": st.column_config.TextColumn("Sumber / Referensi", width="large"),
                "Kategori": st.column_config.TextColumn("Kategori", width="small"),
            },
            use_container_width=True, hide_index=True
        )

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
        if st.button("🎯 Target 5%", use_container_width=True):
            st.session_state.biofuel_val = 5.0
            st.session_state.local_proc_val = 10.0
            st.session_state.modal_shift_val = 10.0
            st.session_state.ev_val = 0.0
            st.toast("Target 5% Reduksi Emisi Berhasil Diterapkan!", icon="🎯")
            st.rerun()
    with col_p2:
        if st.button("🚀 Target 15%", use_container_width=True):
            st.session_state.biofuel_val = 20.0
            st.session_state.local_proc_val = 25.0
            st.session_state.modal_shift_val = 25.0
            st.session_state.ev_val = 5.0
            st.toast("Target 15% Reduksi Emisi Berhasil Diterapkan!", icon="🚀")
            st.rerun()
    with col_p3:
        if st.button("🏆 Target 30% (Net-Zero)", use_container_width=True, type="primary"):
            opt_res = solve_scipy_optimal_decarbonization(
                base_s1, base_s3, NET_ZERO_TARGET_PERCENTAGE, st.session_state.carbon_price_val, dist_km, payload
            )
            if opt_res["success"]:
                st.session_state.biofuel_val = opt_res["biofuel_val"]
                st.session_state.local_proc_val = opt_res["local_proc_val"]
                st.session_state.modal_shift_val = opt_res["modal_shift_val"]
                st.session_state.ev_val = opt_res["ev_val"]
                
                # Check real physical limits hit
                is_maxed_out = (
                    opt_res["biofuel_val"] >= MAX_BIOFUEL_MIX - 1.0 and
                    opt_res["ev_val"] >= MAX_EV_RETROFIT - 1.0 and
                    opt_res["local_proc_val"] >= MAX_LOCAL_PROCUREMENT - 1.0 and
                    opt_res["modal_shift_val"] >= MAX_BARGE_MODAL_SHIFT - 1.0
                )
                
                # We need to manually calculate the real percentage based on discrete slider values
                real_check = calculate_decarbonization(
                    base_s1, base_s3, 
                    opt_res["biofuel_val"], opt_res["local_proc_val"], 
                    opt_res["ev_val"], opt_res["modal_shift_val"], 
                    st.session_state.carbon_price_val, dist_km, payload
                )
                real_pct = real_check['pct_reduction']
                
                if is_maxed_out and real_pct < NET_ZERO_TARGET_PERCENTAGE:
                    st.toast(f"Kapasitas fisik armada sudah maksimal. Reduksi terbaik: {real_pct:.1f}% (Target {NET_ZERO_TARGET_PERCENTAGE}% tidak tercapai)", icon="⚠️")
                else:
                    st.toast(f"Solver selesai. Kapasitas reduksi terbaik: {real_pct:.1f}% (Target: {NET_ZERO_TARGET_PERCENTAGE}%)", icon="✅")
                    
                st.rerun()
            else:
                st.error(f"⚠️ Solver Failed: Tidak dapat menemukan kombinasi optimal yang memenuhi target {NET_ZERO_TARGET_PERCENTAGE}% dengan konstrain saat ini.")
    with col_p4:
        if st.button("🔄 Reset", use_container_width=True):
            st.session_state.biofuel_val, st.session_state.local_proc_val, st.session_state.ev_val, st.session_state.modal_shift_val, st.session_state.carbon_price_val = 0.0, 0.0, 0.0, 0.0, DEFAULT_CARBON_PRICE_USD
            st.rerun()

    st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)

    col_sim1, col_sim2 = st.columns([5, 5])
    with col_sim1:
        st.markdown("""
            <div class="petrosea-callout">
                <h4>Pilih Parameter Dekarbonisasi</h4>
                <p>Atur persentase kebijakan di bawah, atau klik <b>Auto Optimize</b> biar sistem cari kombinasi termurah buat capai target 30%.</p>
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
        sim_res = calculate_decarbonization(
            base_s1, base_s3, biofuel_mix, local_proc_increase, ev_retrofit_pct, modal_shift_barge, carbon_price, dist_km, payload
        )
        
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

