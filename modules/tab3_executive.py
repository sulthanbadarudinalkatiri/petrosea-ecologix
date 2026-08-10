import streamlit as st
import pandas as pd

def render_tab3_executive(df_emissions: pd.DataFrame, df_suppliers: pd.DataFrame, df_routes: pd.DataFrame, selected_year: int, scope3_tot: float, curr_data: pd.Series):
    """
    Renders Tab 3: Board Executive Briefing Statement & Verified Audit Trail Data.
    Designed for Board of Directors decision-makers and external ESG auditors.
    """
    st.subheader("Rangkuman Eksekutif Direksi & Transparansi Data Audit")
    st.caption("Ringkasan eksekutif untuk pengambil keputusan (Board of Directors) yang mengombinasikan proyeksi dekarbonisasi, rekomendasi logistik koridor, serta berkas verifikasi audit data terstruktur.")
    st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 1. EXECUTIVE IMPACT BOARD
    # -------------------------------------------------------------------------
    col_e1, col_e2, col_e3, col_e4 = st.columns(4)
    
    s1_curr = curr_data.get('Scope1_tCO2e', 0.0)
    s2_curr = curr_data.get('Scope2_tCO2e', 0.0)
    total_ops_emissions = s1_curr + s2_curr
    revenue_val = curr_data.get('Revenue_MUSD', 0.0)
    carbon_intensity = (total_ops_emissions / revenue_val) if revenue_val > 0 else 0.0
    
    high_risk_count = len(df_suppliers[df_suppliers['ESG_Score'] < 75])
    local_spend_pct = (df_suppliers[df_suppliers['Location_Type'] == 'Local']['Spend_USD'].sum() / df_suppliers['Spend_USD'].sum() * 100) if df_suppliers['Spend_USD'].sum() > 0 else 0

    with col_e1:
        st.metric(
            label="Total Emisi Operasional (Scope 1 & 2)",
            value=f"{total_ops_emissions:,.2f} tCO2e",
            help="Jumlah emisi langsung dari solar alat berat tambang dan konsumsi listrik operasional situs."
        )
    with col_e2:
        st.metric(
            label="Intensitas Karbon Korporat",
            value=f"{carbon_intensity:.2f} tCO2e/$1M",
            help="Rasio emisi langsung terhadap total pendapatan korporasi PT Petrosea Tbk."
        )
    with col_e3:
        st.metric(
            label="Profil Risiko Pemasok (ESG < 75)",
            value=f"{high_risk_count} Pemasok",
            delta="Perlu Audit" if high_risk_count > 0 else "Kepatuhan Optimal",
            delta_color="inverse"
        )
    with col_e4:
        st.metric(
            label="Realisasi Belanja Pemasok Lokal",
            value=f"{local_spend_pct:.1f}%",
            delta="Target Korporat: 40.0%"
        )

    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 2. BOARD EXECUTIVE BRIEFING STATEMENT (DYNAMIC DUAL-SCENARIO INTEGRATION)
    # -------------------------------------------------------------------------
    non_iso_vendors = len(df_suppliers[df_suppliers['ISO14001_Certified'] == 'No'])
    non_tkdn_vendors = len(df_suppliers[df_suppliers['TKDN_Compliant'] == 'No'])

    locked_logistics = st.session_state.get('locked_logistics', None)
    locked_decarb = st.session_state.get('locked_decarb', None)

    # LOGISTICS SCENARIO TEXT
    if locked_logistics:
        desiccant_cost = locked_logistics.get('desiccant_cost', 0)
        desiccant_str = f" dengan Proteksi Sealed Desiccant Container (<b>${desiccant_cost:,.0f} USD</b>)" if desiccant_cost > 0 else ""
        mode_str = locked_logistics.get('mode_choice', 'Marine Barge (Laut)')
        origin_str = locked_logistics.get('origin', 'Balikpapan')
        dest_str = locked_logistics.get('destination', 'Sorong')
        dist_val = locked_logistics.get('dist_km', 1250)
        lead_val = locked_logistics.get('lead_days', 10)
        emiss_val = locked_logistics.get('est_cargo_emiss', 1.87)
        cargo_str = locked_logistics.get('cargo_type', 'Kargo Sensitif Kelembapan')
        
        logistics_html = (
            f"<b>3. Rekomendasi Logistik Koridor</b> <span style='color: #00A86B; font-size: 0.8rem; font-weight: 600;'>[Terkunci {locked_logistics['timestamp']}]</span>:<br>"
            f"• <b>Koridor Utama</b>: <b>{origin_str} ➔ {dest_str} ({dist_val:,.0f} km)</b><br>"
            f"• <b>Moda Terpilih</b>: <b>{mode_str}</b> (Waktu Transit: <b>{lead_val} Hari</b>, Estimasi Emisi: <b>{emiss_val:,.2f} tCO2e</b>)<br>"
            f"• <b>Spesifikasi Kargo & Proteksi</b>: {cargo_str}{desiccant_str}"
        )
    else:
        logistics_html = (
            "<b>3. Rekomendasi Logistik Koridor</b> <span style='color: #007AFF; font-size: 0.8rem; font-weight: 600;'>[Baseline Standar]</span>:<br>"
            "Gunakan Moda Marine Barge untuk koridor antar-pulau jangka panjang dan pasang kontainer desiccant pada material presisi sensitif kelembapan."
        )

    # DECARBONIZATION SCENARIO TEXT
    if locked_decarb:
        sim = locked_decarb['sim_res']
        decarb_html = (
            f"<b>4. Proyeksi Optimalisasi Dekarbonisasi Tambang</b> <span style='color: #00A86B; font-size: 0.8rem; font-weight: 600;'>[Terkunci {locked_decarb['timestamp']}]</span>:<br>"
            f"• <b>Kombinasi Kebijakan Disetujui</b>: Substitusi Biofuel B100 <b>{locked_decarb['biofuel_val']:.0f}%</b>, Local Sourcing <b>+{locked_decarb['local_proc_val']:.0f}%</b>, Shift Marine Barge <b>{locked_decarb['modal_shift_val']:.0f}%</b>, Retrofit EV <b>{locked_decarb['ev_val']:.0f}%</b><br>"
            f"• <b>Proyeksi Reduksi Emisi & Biaya</b>: Memangkas emisi sebesar <b>{sim['total_abatement']:,.2f} tCO2e/tahun ({sim['pct_reduction']:.1f}% penurunan)</b> dengan estimasi efisiensi penghematan biaya <b>${sim['cost_savings_usd']:,.2f} USD</b><br>"
            f"• <b>Dampak Lingkungan Nyata</b>: Ekuivalen dengan <b>{locked_decarb['trees_count']:,} pohon tropis ditanam</b>, <b>{locked_decarb['trucks_count']:,} truk diesel retired</b>, atau <b>{locked_decarb['homes_count']:,} rumah teraliri listrik bersih</b>."
        )
    else:
        decarb_html = (
            "<b>4. Proyeksi Optimalisasi Dekarbonisasi Tambang</b> <span style='color: #007AFF; font-size: 0.8rem; font-weight: 600;'>[Baseline Standar]</span>:<br>"
            "Jalankan simulasi preskriptif di tab Simulator Rute lalu klik 'Kunci Skenario Dekarbonisasi' untuk menetapkan target kebijakan resmi."
        )

    st.markdown(f"""
        <div class="petrosea-callout">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 10px;">
                <h4 style="margin: 0; font-size: 1.1rem; color: #FFFFFF;">Board of Directors Executive Briefing Statement ({selected_year})</h4>
                <span style='background-color: rgba(0,168,107,0.15); color: #00A86B; padding: 4px 12px; border-radius: 4px; font-size: 0.85rem; font-weight: 600;'>Dual-Scenario Intelligence Locked</span>
            </div>
            <p style="margin-bottom: 10px;"><b>1. Diagnosis Emisi:</b> Total emisi operasional langsung (Scope 1 & 2) tercatat di level <b>{total_ops_emissions:,.2f} tCO2e</b> dengan intensitas emisi <b>{carbon_intensity:.2f} tCO2e/$1M pendapatan</b>. Realisasi pengadaan barang dari vendor lokal berada pada tingkat <b>{local_spend_pct:.1f}%</b>.</p>
            <p style="margin-bottom: 10px;"><b>2. Audit Kepatuhan & Risiko Pemasok:</b> Ditemukan <b>{high_risk_count} pemasok berisiko tinggi</b> (skor ESG di bawah 75), <b>{non_iso_vendors} pemasok</b> belum bersertifikasi ISO 14001, dan <b>{non_tkdn_vendors} pemasok</b> belum memenuhi standar kelayakan TKDN korporat.</p>
            <p style="margin-bottom: 10px;">{logistics_html}</p>
            <p style="margin-top: 10px; margin-bottom: 0;">{decarb_html}</p>
        </div>
    """, unsafe_allow_html=True)


    st.markdown("<div style='margin-bottom: 25px;'></div>", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 3. VERIFIED DATA PROVENANCE & AUDIT TRAIL EXPANDERS
    # -------------------------------------------------------------------------
    st.markdown("### Verifikasi Data Audit & Log Sistem")
    st.caption("Berkas audit mentah, metodologi ekstraksi PDF Laporan Keberlanjutan Petrosea 2025, dan catatan validasi sistem.")

    with st.expander("📁 Metodologi Ekstraksi & Transparansi Data PDF (GRI Disclosures)"):
        st.markdown("""
        * **Sumber Data Utama**: Laporan Keberlanjutan PT Petrosea Tbk 2025 (Official Sustainability Report).
        * **Skrip Ingest & Pipeline**: Berkas `scripts/extract_sr_pdf.py` mengekstrak data kuantitatif PDF menggunakan PyMuPDF & Regex parser.
        * **Validasi Tipe Data**: Modul `modules/data_loader.py` melakukan verifikasi tipe data dan null-check baris demi baris menggunakan skema Pydantic (`modules/schemas.py`).
        * **Cakupan Pengungkapan**: Memencakup emisi Scope 1, Scope 2, Scope 3 (Logistik Hulu, Perjalanan Dinas, Pembelian Barang), profil 10 pemasok utama, serta parameter rute logistik koridor.
        """)

    with st.expander("📊 Tabel Audit Mentah Emisi Historis & Pemasok (CSV Export)"):
        st.dataframe(df_emissions, use_container_width=True, hide_index=True)
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            st.download_button(
                label="Unduh Data Emisi Historis (CSV)",
                data=df_emissions.to_csv(index=False).encode('utf-8'),
                file_name=f"petrosea_emissions_audit_{selected_year}.csv",
                mime="text/csv",
                use_container_width=True
            )
        with col_d2:
            st.download_button(
                label="Unduh Data Pemasok Korporat (CSV)",
                data=df_suppliers.to_csv(index=False).encode('utf-8'),
                file_name="petrosea_suppliers_audit.csv",
                mime="text/csv",
                use_container_width=True
            )

    with st.expander("📋 System Validation Log & Audit Trail (Pydantic Logs)"):
        val_log_content = ""
        try:
            with open("logs/data_validation.log", "r", encoding="utf-8") as f:
                val_log_content = f.read()
        except Exception:
            val_log_content = "Log validasi tidak ditemukan."

        st.code(val_log_content, language="log")
        st.download_button(
            label="Unduh Berkas Log Validasi Pydantic (LOG)",
            data=val_log_content.encode('utf-8'),
            file_name="petrosea_data_validation.log",
            mime="text/plain",
            use_container_width=True
        )
