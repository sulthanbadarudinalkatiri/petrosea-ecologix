import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from modules.schemas import calculate_dynamic_esg_score

def render_tab1(df_emissions: pd.DataFrame, df_suppliers: pd.DataFrame, selected_year: int, scope3_tot: float, curr_data: pd.Series):
    """
    Tampilkan gambaran emisi dan profil risiko pemasok.
    
    Fungsi ini memisahkan emisi langsung operasional (Scope 1 & 2) dari emisi tidak langsung rantai pasok (Scope 3).
    Menyoroti dominasi emisi dari pengadaan Barang & Jasa serta memetakan pemasok yang memiliki skor ESG di bawah standar.
    """
    st.subheader("Apa yang berubah dari emisi & pemasok tahun ini")
    st.caption("Perbandingan emisi dari tahun ke tahun dan pemetaan risiko pemasok PT Petrosea Tbk.")
    st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)
    
    # -------------------------------------------------------------------------
    # 1. TEMUAN UTAMA (INSIGHT NARRATIVE - SO WHAT FIRST)
    # -------------------------------------------------------------------------
    prev_years = df_emissions[df_emissions['Year'] < selected_year]['Year']
    if not prev_years.empty:
        prev_year = prev_years.max()
        prev_row = df_emissions[df_emissions['Year'] == prev_year].iloc[0]
        curr_s1_s2 = curr_data['Scope1_tCO2e'] + curr_data['Scope2_tCO2e']
        prev_s1_s2 = prev_row['Scope1_tCO2e'] + prev_row['Scope2_tCO2e']
        yoy_change = ((curr_s1_s2 - prev_s1_s2) / prev_s1_s2 * 100) if prev_s1_s2 > 0 else 0.0
        direction_text = "penurunan" if yoy_change < 0 else "peningkatan"
        change_badge = f"<b>{abs(yoy_change):.1f}% {direction_text} dibanding {prev_year}</b>"
    else:
        change_badge = "baseline awal"

    s3_categories = {
        "Logistik Hulu": curr_data.get('Scope3_Cat4_UpstreamLogistics_tCO2e', 0.0),
        "Perjalanan Dinas": curr_data.get('Scope3_Cat6_BusinessTravel_tCO2e', 0.0),
        "Barang & Jasa": curr_data.get('Scope3_Cat1_PurchasedGoods_tCO2e', 0.0)
    }
    largest_s3_cat = max(s3_categories, key=s3_categories.get)
    largest_s3_val = s3_categories[largest_s3_cat]
    s3_pct = (largest_s3_val / scope3_tot * 100) if scope3_tot > 0 else 0.0

    high_risk_count = len(df_suppliers[df_suppliers['ESG_Score'] < 75])

    st.markdown(f"""
        <div class="petrosea-callout">
            <h4>Temuan Utama Emisi & Pemasok ({selected_year})</h4>
            <p>• <b>Kategori {largest_s3_cat} menyumbang {s3_pct:.1f}% dari emisi Scope 3</b> ({largest_s3_val:,.2f} tCO2e) — jauh lebih besar dari logistik pengiriman. Ini artinya efisiensi pengiriman saja tidak cukup; yang perlu diubah adalah seleksi vendor pengadaan.</p>
            <p>• <b>Terdeteksi {high_risk_count} pemasok berisiko tinggi</b> dengan skor ESG di bawah 75. Emisi operasional langsung (Scope 1 & 2) mencatatkan {change_badge}.</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 2. METRIC TILES ROW
    # -------------------------------------------------------------------------
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    
    s1_val = curr_data.get('Scope1_tCO2e', 0.0)
    s2_val = curr_data.get('Scope2_tCO2e', 0.0)
    revenue_val = curr_data.get('Revenue_MUSD', 0.0)
    intensity_val = ((s1_val + s2_val) / revenue_val) if revenue_val and revenue_val > 0 else 0.0
    intensity_disp = f"{intensity_val:.2f} tCO2e/$M" if revenue_val and revenue_val > 0 else "N/A"

    with col_m1:
        st.metric(label="Emisi solar alat berat (Scope 1)", value=f"{s1_val:,.2f} tCO2e", help="Hasil pembakaran solar B35/B40 pada unit armada tambang.")
    with col_m2:
        st.metric(label="Emisi listrik fasilitas (Scope 2)", value=f"{s2_val:,.2f} tCO2e", help="Konsumsi listrik PLN di kantor operasional & PSF Balikpapan/Sorong.")
    with col_m3:
        st.metric(label="Emisi pengadaan & logistik (Scope 3)", value=f"{scope3_tot:,.2f} tCO2e", help="Emisi dari pembelian material, angkutan barang, dan perjalanan dinas.")
    with col_m4:
        st.metric(label="Rasio emisi per pendapatan", value=intensity_disp, help="Rasio emisi langsung Scope 1+2 untuk setiap 1 juta USD pendapatan.")

    st.markdown("<div style='margin-bottom: 25px;'></div>", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 3. EMISSION TREND & SCOPE 3 DECOMPOSITION
    # -------------------------------------------------------------------------
    col_a, col_b = st.columns([6, 4])
    
    with col_a:
        df_chart = df_emissions.copy()
        df_chart['Scope3_Total'] = (
            df_chart['Scope3_Cat4_UpstreamLogistics_tCO2e'] + 
            df_chart['Scope3_Cat6_BusinessTravel_tCO2e'] + 
            df_chart['Scope3_Cat1_PurchasedGoods_tCO2e']
        )
        df_chart['Intensity'] = (df_chart['Scope1_tCO2e'] + df_chart['Scope2_tCO2e']) / df_chart['Revenue_MUSD']

        fig_combo = make_subplots(specs=[[{"secondary_y": True}]])
        fig_combo.add_trace(
            go.Bar(
                x=df_chart['Year'].astype(str), 
                y=df_chart['Scope1_tCO2e'], 
                name="Scope 1 (Bahan Bakar)",
                marker_color="#E87722",
                hovertemplate="%{x} Scope 1: <b>%{y:,.2f} tCO2e</b>"
            ),
            secondary_y=False
        )
        fig_combo.add_trace(
            go.Bar(
                x=df_chart['Year'].astype(str), 
                y=df_chart['Scope2_tCO2e'], 
                name="Scope 2 (Listrik)",
                marker_color="#0284C7",
                hovertemplate="%{x} Scope 2: <b>%{y:,.2f} tCO2e</b>"
            ),
            secondary_y=False
        )
        fig_combo.add_trace(
            go.Bar(
                x=df_chart['Year'].astype(str), 
                y=df_chart['Scope3_Total'], 
                name="Scope 3 (Rantai Pasok)",
                marker_color="#005A36",
                hovertemplate="%{x} Scope 3: <b>%{y:,.2f} tCO2e</b>"
            ),
            secondary_y=False
        )
        fig_combo.add_trace(
            go.Scatter(
                x=df_chart['Year'].astype(str), 
                y=df_chart['Intensity'], 
                name="Intensitas Karbon",
                mode="lines+markers",
                line=dict(color="#F59E0B", width=3.5),
                marker=dict(size=9, color="#F59E0B"),
                hovertemplate="%{x} Intensitas: <b>%{y:.2f} tCO2e/$M</b>"
            ),
            secondary_y=True
        )

        fig_combo.update_layout(
            barmode='stack',
            title=dict(text="<b>Tren Emisi & Intensitas Karbon per Tahun</b>", font=dict(size=14)),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            hovermode="x unified",
            margin=dict(l=20, r=20, t=50, b=60),
            legend=dict(orientation="h", yanchor="top", y=-0.22, xanchor="center", x=0.5, font=dict(size=10))
        )
        fig_combo.update_xaxes(type='category', title=dict(text="Tahun"))
        fig_combo.update_yaxes(title=dict(text="Emisi (tCO2e)"), secondary_y=False, gridcolor="rgba(0,90,54,0.15)")
        fig_combo.update_yaxes(title=dict(text="Intensitas (tCO2e/$M)"), secondary_y=True, showgrid=False)

        st.plotly_chart(fig_combo, use_container_width=True)

    with col_b:
        labels = ["Logistik Hulu", "Perjalanan Dinas", "Barang & Jasa"]
        values = [
            curr_data['Scope3_Cat4_UpstreamLogistics_tCO2e'],
            curr_data['Scope3_Cat6_BusinessTravel_tCO2e'],
            curr_data['Scope3_Cat1_PurchasedGoods_tCO2e']
        ]
        
        fig_donut = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=.62,
            marker=dict(colors=['#005A36', '#5A6862', '#E87722']),
            hovertemplate="%{label}: <b>%{value:,.2f} tCO2e</b> (%{percent})"
        )])
        
        fig_donut.update_layout(
            title=dict(text=f"<b>Proporsi Emisi Scope 3 ({selected_year})</b>", font=dict(size=14)),
            annotations=[dict(text=f"<b>Scope 3</b><br><span>{scope3_tot:,.0f} tCO2e</span>", x=0.5, y=0.5, font_size=13, showarrow=False)],
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=10, r=10, t=50, b=60),
            legend=dict(orientation="h", yanchor="top", y=-0.22, xanchor="center", x=0.5, font=dict(size=10))
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    st.markdown("---")

    # -------------------------------------------------------------------------
    # 4. SUPPLIER ESG RISK MATRIX & VENDOR BENCHMARK RADAR
    # -------------------------------------------------------------------------
    st.markdown("### Pemasok mana yang perlu diaudit sekarang")
    st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)

    col_s1, col_s2 = st.columns([6, 4])
    
    with col_s1:
        df_suppliers_fmt = df_suppliers.copy()
        df_suppliers_fmt['Spend_Formatted'] = df_suppliers_fmt['Spend_USD'].apply(
            lambda x: f"${x/1e6:.2f}M" if x >= 1e6 else f"${x/1e3:.0f}K"
        )
        color_map = {'Local': '#00875A', 'Non-Local National': '#F59E0B', 'International': '#0284C7'}

        fig_scatter = px.scatter(
            df_suppliers_fmt, 
            x="Spend_USD", 
            y="ESG_Score",
            size="Carbon_Intensity_kgCO2_per_USD", 
            color="Location_Type",
            hover_name="Supplier_Name", 
            hover_data={"Supplier_ID": True, "Spend_Formatted": True, "Spend_USD": False, "Category": True},
            title="<b>Sebaran Pemasok: Total Belanja vs Skor ESG</b>",
            labels={"Spend_USD": "Total Belanja (USD)", "ESG_Score": "Skor ESG (0-100)", "Location_Type": "Lokasi Vendor"},
            color_discrete_map=color_map,
            size_max=26
        )
        fig_scatter.add_hline(y=75, line_dash="dash", line_color="#D9381E", annotation_text="Batas Aman Skor ESG (75)")
        fig_scatter.update_traces(marker=dict(opacity=0.85, line=dict(width=1.5, color='#FFFFFF')))
        fig_scatter.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)', 
            margin=dict(l=20, r=20, t=50, b=50),
            legend=dict(orientation="h", yanchor="top", y=-0.22, xanchor="center", x=0.5, font=dict(size=10))
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    with col_s2:
        st.markdown("#### Detail Profil ESG Pemasok")
        if df_suppliers.empty:
            st.warning("Data pemasok belum tersedia di folder /data — jalankan skrip ekstraksi PDF terlebih dahulu.")
        else:
            from modules.constants import MAX_BENCHMARK_LEAD_TIME_DAYS, MAX_BENCHMARK_CARBON_INTENSITY
            
            selected_vendor = st.selectbox("Pilih Pemasok", df_suppliers['Supplier_Name'].unique(), key="vendor_select_tab1")
            vendor_info = df_suppliers[df_suppliers['Supplier_Name'] == selected_vendor].iloc[0]
            
            dynamic_score = calculate_dynamic_esg_score(
                base_esg=float(vendor_info['ESG_Score']),
                iso_certified=str(vendor_info['ISO14001_Certified']),
                tkdn_compliant=str(vendor_info['TKDN_Compliant']),
                carbon_intensity=float(vendor_info['Carbon_Intensity_kgCO2_per_USD']),
                lead_time_days=int(vendor_info['Delivery_LeadTime_Days'])
            )
            
            loc_type = vendor_info['Location_Type']
            assigned_color = '#00875A' if loc_type == 'Local' else ('#F59E0B' if loc_type == 'Non-Local National' else '#0284C7')

            with st.container(border=True):
                st.markdown(f"**{vendor_info['Supplier_Name']}** ({vendor_info['Supplier_ID']})")
                spend_txt = f"${vendor_info['Spend_USD']/1e6:.2f} Juta" if vendor_info['Spend_USD'] >= 1e6 else f"${vendor_info['Spend_USD']/1e3:.0f} Ribu"
                st.caption(f"Belanja: **{spend_txt}** | Waktu Pengiriman: **{vendor_info['Delivery_LeadTime_Days']} Hari** | Skor Evaluasi: **{dynamic_score:.1f}/100**")

            categories = ['Skor ESG', 'TKDN', 'ISO 14001', 'Efisiensi Karbon', 'Efisiensi Waktu']
            tkdn_val = 100.0 if str(vendor_info['TKDN_Compliant']).upper() in ['YES', 'TRUE', 'Y'] else 40.0
            iso_val = 100.0 if str(vendor_info['ISO14001_Certified']).upper() in ['YES', 'TRUE', 'Y'] else 30.0
            
            c_int = float(vendor_info['Carbon_Intensity_kgCO2_per_USD'])
            carbon_eff = max(0.0, min(100.0, (1.0 - (c_int / MAX_BENCHMARK_CARBON_INTENSITY)) * 100.0))
            
            lt_days = int(vendor_info['Delivery_LeadTime_Days'])
            lead_eff = max(0.0, min(100.0, (1.0 - (lt_days / MAX_BENCHMARK_LEAD_TIME_DAYS)) * 100.0))
            
            scores = [float(vendor_info['ESG_Score']), tkdn_val, iso_val, carbon_eff, lead_eff]
            
            fig_radar = go.Figure(data=go.Scatterpolar(
                r=scores, theta=categories, fill='toself', name=vendor_info['Supplier_Name'],
                line=dict(color=assigned_color, width=3), fillcolor=assigned_color, opacity=0.35
            ))
            fig_radar.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100]), angularaxis=dict(tickfont=dict(size=10))),
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False,
                margin=dict(l=30, r=30, t=30, b=20)
            )
            st.plotly_chart(fig_radar, use_container_width=True)

    # -------------------------------------------------------------------------
    # 5. RECOMMENDATION ACTION MATRIX TABLE
    # -------------------------------------------------------------------------
    st.markdown("### Tindakan perbaikan untuk pemasok yang belum memenuhi standar")
    
    def generate_rec(row):
        actions = []
        if row['ESG_Score'] < 75: actions.append("Audit ESG Khusus")
        if row['ISO14001_Certified'] == 'No': actions.append("Wajibkan ISO 14001")
        if row['TKDN_Compliant'] == 'No': actions.append("Tingkatkan Komponen Lokal")
        if row['Location_Type'] != 'Local': actions.append("Prioritaskan Pemasok Lokal")
        return " | ".join(actions) if actions else "Sudah Memenuhi Semua Kriteria"

    df_action = df_suppliers.copy()
    df_action['Status_Rekomendasi'] = df_action.apply(generate_rec, axis=1)
    
    st.dataframe(
        df_action[['Supplier_ID', 'Supplier_Name', 'Category', 'Location_Type', 'ESG_Score', 'TKDN_Compliant', 'ISO14001_Certified', 'Status_Rekomendasi']],
        column_config={
            "Supplier_ID": st.column_config.TextColumn("ID Vendor", width="small"),
            "Supplier_Name": "Nama Pemasok",
            "Category": "Kategori",
            "Location_Type": "Lokasi Pemasok",
            "ESG_Score": st.column_config.ProgressColumn("Skor ESG", format="%d", min_value=0, max_value=100),
            "TKDN_Compliant": "TKDN",
            "ISO14001_Certified": "ISO 14001",
            "Status_Rekomendasi": "Tindakan Perbaikan yang Diperlukan"
        },
        use_container_width=True, hide_index=True
    )

    st.download_button(
        label="Unduh Scorecard Pemasok (CSV)",
        data=df_suppliers.to_csv(index=False).encode('utf-8'),
        file_name="petrosea_suppliers_scorecard.csv",
        mime="text/csv"
    )

    # -------------------------------------------------------------------------
    # CONTEXTUAL BRIDGE CTA TO TAB 2 (NARRATIVE MOMENTUM) & SOURCE CITATION
    # -------------------------------------------------------------------------
    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)
    st.info(
        f"💡 **Langkah Selanjutnya**: Terdeteksi **{high_risk_count} pemasok berisiko tinggi** dan **{s3_pct:.1f}% emisi Scope 3** yang terkonsentrasi di pengadaan. "
        "Lihat prakiraan cuaca rute 7 hari ke depan & hitung opsi perbaikannya di tab **Simulator Rute** →"
    )

