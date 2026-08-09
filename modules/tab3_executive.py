import streamlit as st
import pandas as pd

def render_tab3_executive(df_emissions: pd.DataFrame, df_suppliers: pd.DataFrame, df_routes: pd.DataFrame, selected_year: int, scope3_tot: float, curr_data: pd.Series):
    """
    Tampilkan ringkasan naratif untuk jajaran direksi dan sediakan file data audit.
    
    Fungsi ini merangkum temuan emisi dan risiko pemasok menjadi 3 langkah narasi (Diagnosis, Risiko, Rekomendasi).
    Juga menyediakan akses langsung ke tabel data mentah dan tombol unduh CSV untuk kebutuhan audit eksternal.
    """
    st.subheader("Rangkuman untuk direksi & data audit")
    st.caption("Ringkasan hasil analisis emisi, pemetaan risiko pemasok, dan unduh data audit PT Petrosea Tbk.")
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
        st.metric(label="Total emisi Scope 1 & 2", value=f"{total_ops_emissions:,.2f} tCO2e", help="Emisi dari penggunaan bahan bakar solar alat berat dan listrik operasional.")
    with col_e2:
        st.metric(label="Intensitas emisi per pendapatan", value=f"{carbon_intensity:.2f} tCO2e/$M", help="Rasio emisi langsung terhadap total pendapatan korporasi.")
    with col_e3:
        st.metric(label="Pemasok berisiko tinggi (ESG < 75)", value=f"{high_risk_count} Pemasok", delta="Perlu Audit" if high_risk_count > 0 else "Aman", delta_color="inverse")
    with col_e4:
        st.metric(label="Persentase belanja dari vendor lokal", value=f"{local_spend_pct:.1f}%", delta="Target: 40%")

    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 2. BOARD EXECUTIVE BRIEFING (DYNAMIC LOCKED SCENARIO INTEGRATION)
    # -------------------------------------------------------------------------
    non_iso_vendors = len(df_suppliers[df_suppliers['ISO14001_Certified'] == 'No'])
    non_tkdn_vendors = len(df_suppliers[df_suppliers['TKDN_Compliant'] == 'No'])

    locked_logistics = st.session_state.get('locked_logistics', None)
    locked_decarb = st.session_state.get('locked_decarb', None)

    # 3A. LOGISTICS SCENARIO TEXT
    if locked_logistics:
        desiccant_cost = locked_logistics.get('desiccant_cost', 0)
        desiccant_str = f" dengan Proteksi Sealed Desiccant Container <b>${desiccant_cost:,.0f} USD</b>" if desiccant_cost > 0 else ""
        mode_str = locked_logistics.get('mode_choice', 'Marine Barge (Laut)')
        origin_str = locked_logistics.get('origin', 'Balikpapan')
        dest_str = locked_logistics.get('destination', 'Sorong')
        dist_val = locked_logistics.get('dist_km', 1250)
        lead_val = locked_logistics.get('lead_days', 10)
        emiss_val = locked_logistics.get('est_cargo_emiss', 1.87)
        cargo_str = locked_logistics.get('cargo_type', 'Kargo Sensitif Kelembapan')
        
        logistics_text = (
            f"<b>3A. Rekomendasi Logistik Koridor</b> <span style='color: #00A86B; font-size: 0.8rem;'>[Terkunci {locked_logistics['timestamp']}]</span>:<br>"
            f"• <b>Koridor Pengiriman</b>: <b>{origin_str} ➔ {dest_str} ({dist_val:,.0f} km)</b><br>"
            f"• <b>Moda Utama</b>: <b>{mode_str}</b> (Transit: <b>{lead_val} Hari</b>, Estimasi Emisi: <b>{emiss_val:,.2f} tCO2e</b>)<br>"
            f"• <b>Proteksi Material Presisi</b>: {cargo_str}{desiccant_str}"
        )
    else:
        logistics_text = (
            "<b>3A. Rekomendasi Logistik Koridor</b> <span style='color: #007AFF; font-size: 0.8rem;'>[Baseline Standar]</span>:<br>"
            "Gunakan Moda Marine Barge untuk koridor antar-pulau jangka panjang dan pasang kontainer desiccant pada material presisi."
        )

    # 3B. DECARBONIZATION SCENARIO TEXT
    if locked_decarb:
        sim = locked_decarb['sim_res']
        decarb_text = (
            f"<b>3B. Proyeksi Dekarbonisasi Tambang</b> <span style='color: #00A86B; font-size: 0.8rem;'>[Terkunci {locked_decarb['timestamp']}]</span>:<br>"
            f"• <b>Kebijakan Disetujui</b>: Biofuel B100 <b>{locked_decarb['biofuel_val']:.0f}%</b>, Local Sourcing <b>+{locked_decarb['local_proc_val']:.0f}%</b>, Marine Barge <b>{locked_decarb['modal_shift_val']:.0f}%</b>, EV Retrofit <b>{locked_decarb['ev_val']:.0f}%</b><br>"
            f"• <b>Potensi Reduksi Emisi</b>: Memangkas <b>{sim['total_abatement']:,.2f} tCO2e/tahun ({sim['pct_reduction']:.1f}% penurunan)</b> dengan efisiensi biaya <b>${sim['cost_savings_usd']:,.2f} USD</b><br>"
            f"• <b>Dampak Lingkungan Nyata</b>: Setara <b>{locked_decarb['trees_count']:,} pohon tropis</b>, <b>{locked_decarb['trucks_count']:,} truk retired</b>, atau <b>{locked_decarb['homes_count']:,} rumah teraliri listrik bersih</b>."
        )
    else:
        decarb_text = (
            "<b>3B. Proyeksi Dekarbonisasi Tambang</b> <span style='color: #007AFF; font-size: 0.8rem;'>[Baseline Standar]</span>:<br>"
            "Jalankan simulasi di tab Simulator Rute lalu klik 'Kunci Skenario Dekarbonisasi' untuk mengunci target kebijakan khusus."
        )

    st.markdown(f"""
        <div class="petrosea-callout">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <h4 style="margin: 0;">Board of Directors Executive Briefing Statement ({selected_year})</h4>
                <span style='background-color: rgba(0,168,107,0.15); color: #00A86B; padding: 4px 10px; border-radius: 4px; font-size: 0.85rem; font-weight: 600;'>Dual-Scenario Intelligence Mode</span>
            </div>
            <p><b>1. Diagnosis Emisi:</b> Total emisi operasional (Scope 1 & 2) berada di level <b>{total_ops_emissions:,.2f} tCO2e</b> dengan intensitas <b>{carbon_intensity:.2f} tCO2e/$1M pendapatan</b>. Porsi pengadaan lokal saat ini sebesar <b>{local_spend_pct:.1f}%</b>.</p>
            <p><b>2. Risiko Pemasok:</b> Ditemukan <b>{high_risk_count} pemasok berisiko tinggi</b> (skor ESG di bawah 75), <b>{non_iso_vendors} pemasok</b> belum bersertifikat ISO 14001, dan <b>{non_tkdn_vendors} pemasok</b> belum memenuhi standar TKDN minimal.</p>
            <p>{logistics_text}</p>
            <p style="margin-top: 10px;">{decarb_text}</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 3. VERIFIED DATA PROVENANCE & AUDIT TRAIL EXPANDERS
    # -------------------------------------------------------------------------
    with st.expander("Sumber Data & Metode Ekstraksi"):
        st.markdown("""
        * **Sumber Data**: Laporan Keberlanjutan PT Petrosea Tbk 2025.
        * **Skrip Ekstraksi**: `scripts/extract_sr_pdf.py` mengekstrak teks mentah PDF menggunakan PyMuPDF & Regex.
        * **Validasi Tipe Data**: `modules/data_loader.py` memeriksa kesesuaian tipe data baris demi baris lewat Pydantic.
        * **Cakupan Data**: Emisi Scope 1, Scope 2, Scope 3 (Logistik Hulu, Perjalanan Dinas, Pembelian Barang), serta data 10 vendor utama dan rute pengiriman.
        """)

    with st.expander("Tabel Data Mentah Emisi Histori (Audit Trail)"):
        st.dataframe(df_emissions, use_container_width=True, hide_index=True)
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            st.download_button(
                label="Unduh Data Emisi Histori (CSV)",
                data=df_emissions.to_csv(index=False).encode('utf-8'),
                file_name=f"petrosea_emissions_audit_{selected_year}.csv",
                mime="text/csv",
                use_container_width=True
            )
        with col_d2:
            st.download_button(
                label="Unduh Data Pemasok (CSV)",
                data=df_suppliers.to_csv(index=False).encode('utf-8'),
                file_name="petrosea_suppliers_audit.csv",
                mime="text/csv",
                use_container_width=True
            )

    with st.expander("Log Validasi System & Audit Ekstraksi PDF"):
        val_log_content = ""
        try:
            with open("logs/data_validation.log", "r", encoding="utf-8") as f:
                val_log_content = f.read()
        except Exception:
            val_log_content = "Log tidak ditemukan."

        st.code(val_log_content, language="log")
        st.download_button(
            label="Unduh Log Validasi Pydantic (LOG)",
            data=val_log_content.encode('utf-8'),
            file_name="petrosea_data_validation.log",
            mime="text/plain",
            use_container_width=True
        )
