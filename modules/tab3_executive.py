import streamlit as st
import pandas as pd

def render_tab3_executive(df_emissions: pd.DataFrame, df_suppliers: pd.DataFrame, df_routes: pd.DataFrame, selected_year: int, scope3_tot: float, curr_data: pd.Series):
    """
    Renders Tab 3: Board Executive Briefing Statement & Verified Audit Trail Data.
    Designed for Board of Directors decision-makers and external ESG auditors.
    Single Unified Clean Executive Briefing Memo.
    """
    st.subheader("Rangkuman Eksekutif Direksi & Transparansi Data Audit")
    st.caption("Menggabungkan proyeksi dekarbonisasi akurat, rekomendasi logistik koridor, dan verifikasi data audit ESG. Strategi terintegrasi untuk keberlanjutan bisnis.")
    st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)

    locked_logistics = st.session_state.get('locked_logistics', None)
    locked_decarb = st.session_state.get('locked_decarb', None)

    # -------------------------------------------------------------------------
    # 1. EXECUTIVE IMPACT BOARD METRICS WITH VISUAL GAUGE
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
            help="Emisi langsung dari solar alat berat tambang & konsumsi listrik situs."
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
            delta="Perlu Audit ESG" if high_risk_count > 0 else "Kepatuhan Optimal",
            delta_color="inverse"
        )
    with col_e4:
        st.metric(
            label="Realisasi Belanja Pemasok Lokal",
            value=f"{local_spend_pct:.1f}%",
            delta="Target Korporat: 40.0%"
        )
        st.progress(min(local_spend_pct / 40.0, 1.0))

    st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 2. SINGLE UNIFIED EXECUTIVE BRIEFING MEMO CARD
    # -------------------------------------------------------------------------
    non_iso_vendors = len(df_suppliers[df_suppliers['ISO14001_Certified'] == 'No'])
    non_tkdn_vendors = len(df_suppliers[df_suppliers['TKDN_Compliant'] == 'No'])

    # Status Badge Header HTML
    if locked_decarb:
        status_badge_html = "<span style='background-color: #005A36; color: #FFFFFF; font-size: 0.75rem; font-weight: 700; padding: 6px 14px; border-radius: 20px;'>● TARGET TERKUNCI</span>"
    else:
        status_badge_html = "<span style='background-color: #E87722; color: #FFFFFF; font-size: 0.75rem; font-weight: 700; padding: 6px 14px; border-radius: 20px;'>○ BASELINE STANDAR</span>"

    # Logistics HTML Content
    if locked_logistics:
        desiccant_cost = locked_logistics.get('desiccant_cost', 0)
        desiccant_str = f" dengan Proteksi Sealed Desiccant Container System (<b>${desiccant_cost:,.0f} USD</b>)" if desiccant_cost > 0 else ""
        mode_str = locked_logistics.get('mode_choice', 'Marine Barge (Laut)')
        origin_str = locked_logistics.get('origin', 'Balikpapan')
        dest_str = locked_logistics.get('destination', 'Sorong')
        dist_val = locked_logistics.get('dist_km', 1250)
        lead_val = locked_logistics.get('lead_days', 10)
        emiss_val = locked_logistics.get('est_cargo_emiss', 1.87)
        cargo_str = locked_logistics.get('cargo_type', 'Kargo Sensitif Kelembapan')
        
        logistics_inner_html = (
            f"<p style='margin-bottom: 6px; font-size: 0.93rem; line-height: 1.5;'>• <b>Rute Koridor Utama</b>: <b>{origin_str} ➔ {dest_str} ({dist_val:,.0f} km)</b> [Terkunci: {locked_logistics['timestamp']}]</p>"
            f"<p style='margin-bottom: 6px; font-size: 0.93rem; line-height: 1.5;'>• <b>Moda Terpilih & Dampak</b>: <b>{mode_str}</b> (Waktu Transit: <b>{lead_val} Hari</b>, Proyeksi Emisi Kargo: <b>{emiss_val:,.2f} tCO2e</b>).</p>"
            f"<p style='margin-bottom: 0; font-size: 0.93rem; line-height: 1.5;'>• <b>Mitigasi Kargo</b>: Kategori <b>{cargo_str}</b>{desiccant_str}.</p>"
        )
    else:
        logistics_inner_html = (
            "<p style='margin-bottom: 6px; font-size: 0.93rem; line-height: 1.5;'>• <b>Strategi Moda Rantai Pasok</b>: Transisi penuh ke moda <b>Marine Barge (Laut)</b> untuk pengiriman material berat antar-pulau guna meminimalkan biaya logistik & emisi Scope 3.</p>"
            "<p style='margin-bottom: 0; font-size: 0.93rem; line-height: 1.5;'>• <b>Proteksi Risiko Kargo</b>: Pengaplikasian <i>Sealed Desiccant Container System</i> untuk mengamankan sparepart presisi dari kelembapan iklim tropis.</p>"
        )

    # Decarbonization HTML Content
    if locked_decarb:
        sim = locked_decarb['sim_res']
        decarb_inner_html = (
            f"<p style='margin-bottom: 6px; font-size: 0.93rem; line-height: 1.5;'>• <b>Bauran Kebijakan Disetujui</b>: Substitusi Biofuel <b>{locked_decarb['biofuel_val']:.0f}%</b>, Belanja Lokal <b>+{locked_decarb['local_proc_val']:.0f}%</b>, Shift Laut <b>{locked_decarb['modal_shift_val']:.0f}%</b>, & EV Fleet <b>{locked_decarb['ev_val']:.0f}%</b> [Terkunci: {locked_decarb['timestamp']}].</p>"
            f"<p style='margin-bottom: 6px; font-size: 0.93rem; line-height: 1.5;'>• <b>Target Reduksi & Efisiensi</b>: Memangkas emisi operasional sebesar <b>{sim['total_abatement']:,.2f} tCO2e/tahun ({sim['pct_reduction']:.1f}% penurunan)</b> serta penghematan biaya <b>${sim['cost_savings_usd']:,.2f} USD</b>.</p>"
            f"<p style='margin-bottom: 0; font-size: 0.93rem; line-height: 1.5;'>• <b>Ekuivalensi Dampak Lingkungan</b>: Setara dengan <b>{locked_decarb['trees_count']:,} pohon tropis ditanam</b>, <b>{locked_decarb['trucks_count']:,} truk diesel retired</b>, atau listrik bersih bagi <b>{locked_decarb['homes_count']:,} rumah</b>.</p>"
        )
    else:
        decarb_inner_html = (
            "<p style='margin-bottom: 6px; font-size: 0.93rem; line-height: 1.5;'>• <b>Status Skenario</b>: Masih Menggunakan Baseline Standar Operasional (Belum Ada Target Kebijakan Terkunci).</p>"
            "<p style='margin-bottom: 0; font-size: 0.93rem; line-height: 1.5;'>• <b>Rekomendasi Keputusan Rapat</b>: Silakan jalankan simulasi di tab <b>Simulator Rute</b> dan tekan tombol <i>'Kunci Skenario Dekarbonisasi'</i> untuk menetapkan target resmi Direksi.</p>"
        )

    # Render Unified Memo Card
    st.markdown(f"""<div class="petrosea-callout" style="padding: 24px; border-radius: 16px; margin-bottom: 24px;">
<div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid var(--border-color, rgba(0,90,54,0.15)); padding-bottom: 12px; margin-bottom: 16px;">
    <div>
        <h3 style="margin: 0; font-size: 1.15rem; color: #005A36; font-weight: 800;">📄 MEMORANDUM HASIL AUDIT & KEPUTUSAN STRATEGIS DIREKSI</h3>
        <p style="margin: 4px 0 0 0; font-size: 0.85rem; color: var(--text-color); opacity: 0.8;">Ringkasan Eksekutif Terpadu PT Petrosea Tbk — Tahun Operasional {selected_year}</p>
    </div>
    <div>
        {status_badge_html}
    </div>
</div>

<div style="margin-bottom: 16px;">
    <h4 style="margin: 0 0 8px 0; font-size: 0.98rem; color: #E87722; font-weight: 700;">1. Diagnosis Emisi Operasional & Kepatuhan Pemasok (Scope 1, 2, 3)</h4>
    <p style="margin-bottom: 6px; font-size: 0.93rem; line-height: 1.5;">• <b>Profil Emisi Direct & Indirect</b>: Total emisi operasional (Scope 1 & Scope 2) tercatat sebesar <b>{total_ops_emissions:,.2f} tCO2e</b> (Intensitas: <b>{carbon_intensity:.2f} tCO2e/$1M Pendapatan</b>).</p>
    <p style="margin-bottom: 6px; font-size: 0.93rem; line-height: 1.5;">• <b>Realisasi Belanja Lokal</b>: Pencapaian belanja pemasok lokal berada di tingkat <b>{local_spend_pct:.1f}%</b> (Target Korporat: 40.0%).</p>
    <p style="margin-bottom: 0; font-size: 0.93rem; line-height: 1.5;">• <b>Risiko Kepatuhan Rantai Pasok</b>: Teridentifikasi <b style="color:#E87722;">{high_risk_count} pemasok berisiko tinggi</b> (ESG &lt; 75), <b>{non_iso_vendors} vendor</b> non-ISO 14001, serta <b>{non_tkdn_vendors} vendor</b> belum memenuhi standar TKDN.</p>
</div>

<hr style="border: 0; border-top: 1px dashed var(--border-color, rgba(0,0,0,0.12)); margin: 16px 0;">

<div style="margin-bottom: 16px;">
    <h4 style="margin: 0 0 8px 0; font-size: 0.98rem; color: #E87722; font-weight: 700;">2. Rekomendasi Rantai Pasok & Logistik Koridor Utama</h4>
    {logistics_inner_html}
</div>

<hr style="border: 0; border-top: 1px dashed var(--border-color, rgba(0,0,0,0.12)); margin: 16px 0;">

<div>
    <h4 style="margin: 0 0 8px 0; font-size: 0.98rem; color: #E87722; font-weight: 700;">3. Proyeksi Kebijakan Dekarbonisasi Tambang (Keputusan Rapat Direksi)</h4>
    {decarb_inner_html}
</div>
</div>""", unsafe_allow_html=True)

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

