import streamlit as st
import pandas as pd
import html
from modules.constants import DEFAULT_CARBON_PRICE_USD

def render_tab3_executive(df_emissions: pd.DataFrame, df_suppliers: pd.DataFrame, df_routes: pd.DataFrame, selected_year: int, scope3_tot: float, curr_data: pd.Series):
    # Ngambil state dari Tab 2
    locked_logistics = st.session_state.get('locked_logistics', None)
    locked_decarb = st.session_state.get('locked_decarb', None)

    # -------------------------------------------------------------------------
    # 1. STATUS BADGE & JUDUL
    # -------------------------------------------------------------------------
    col_title, col_badge = st.columns([5, 1])
    with col_title:
        st.subheader("Ringkasan Eksekutif & Keputusan")
        st.caption(f"Rekap data operasional tahun {selected_year} dan rekomendasi strategis.")
    with col_badge:
        st.markdown("") # Spacer
        if locked_decarb:
            st.markdown('<div style="text-align: right;"><span style="background-color: #005A36; color: #FFFFFF; font-size: 0.75rem; font-weight: 700; padding: 6px 12px; border-radius: 20px;">● FINAL</span></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="text-align: right;"><span style="background-color: #E87722; color: #FFFFFF; font-size: 0.75rem; font-weight: 700; padding: 6px 12px; border-radius: 20px;">○ DRAFT</span></div>', unsafe_allow_html=True)

    st.divider()

    # -------------------------------------------------------------------------
    # 2. KOMPARASI EKSPOSUR PAJAK KARBON (Side-by-Side)
    # -------------------------------------------------------------------------
    s1_curr = curr_data.get('Scope1_tCO2e', 0.0)
    s2_curr = curr_data.get('Scope2_tCO2e', 0.0)
    total_ops_emissions = s1_curr + s2_curr
    
    # Baseline
    baseline_carbon_tax = total_ops_emissions * DEFAULT_CARBON_PRICE_USD
    
    # Post-Mitigation
    post_emissions = total_ops_emissions
    if locked_decarb:
        post_emissions = total_ops_emissions - locked_decarb['sim_res']['total_abatement']
        if post_emissions < 0: post_emissions = 0.0
    post_carbon_tax = post_emissions * DEFAULT_CARBON_PRICE_USD
    tax_savings = baseline_carbon_tax - post_carbon_tax

    st.markdown("### Eksposur Pajak Karbon & Kepatuhan")
    
    col_kiri, col_kanan = st.columns(2)
    
    with col_kiri:
        st.markdown("""
        <div style="padding: 16px; border: 1px solid rgba(235, 87, 87, 0.3); border-radius: 8px; background-color: rgba(235, 87, 87, 0.05); height: 100%;">
            <h4 style="color: #FF4D4D; margin-top: 0; font-size: 1.1rem;">Kondisi Saat Ini (Do-Nothing)</h4>
            <p style="font-size: 0.9rem; color: var(--text-color); opacity: 0.9;">Total Emisi Baseline:<br><strong style="font-size: 1.2rem;">{:,.2f} tCO2e</strong></p>
            <p style="font-size: 0.9rem; color: var(--text-color); opacity: 0.9;">Kewajiban Pajak Karbon (UU HPP):<br><strong style="font-size: 1.2rem; color: #FF4D4D;">${:,.2f}</strong></p>
        </div>
        """.format(total_ops_emissions, baseline_carbon_tax), unsafe_allow_html=True)

    with col_kanan:
        if locked_decarb:
            st.markdown("""
            <div style="padding: 16px; border: 1px solid rgba(39, 174, 96, 0.3); border-radius: 8px; background-color: rgba(39, 174, 96, 0.05); height: 100%;">
                <h4 style="color: #27AE60; margin-top: 0; font-size: 1.1rem;">Kondisi Pasca-Mitigasi (Skenario Disetujui)</h4>
                <p style="font-size: 0.9rem; color: var(--text-color); opacity: 0.9;">Total Emisi Tereduksi:<br><strong style="font-size: 1.2rem;">{:,.2f} tCO2e</strong></p>
                <p style="font-size: 0.9rem; color: var(--text-color); opacity: 0.9;">Kewajiban Pajak Baru:<br><strong style="font-size: 1.2rem; color: #27AE60;">${:,.2f}</strong></p>
            </div>
            """.format(post_emissions, post_carbon_tax), unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="padding: 16px; border: 1px dashed gray; border-radius: 8px; height: 100%; display: flex; align-items: center; justify-content: center;">
                <p style="font-size: 0.9rem; color: gray; text-align: center; margin: 0;"><em>Skenario belum dikunci di Tab 2.<br>Lakukan simulasi untuk melihat dampak mitigasi.</em></p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)
    
    if locked_decarb:
        st.success(f"**Ringkasan Finansial:** Intervensi ini mengamankan *bottom-line* perusahaan dengan memangkas kewajiban pajak karbon sebesar **${tax_savings:,.2f}** per tahun.")
    else:
        st.warning("**Perhatian:** Tanpa intervensi, eksposur pajak karbon kita berada di level maksimum.")

    st.divider()

    # -------------------------------------------------------------------------
    # 3. KEPUTUSAN OPERASIONAL & KESIAPAN VENDOR
    # -------------------------------------------------------------------------
    high_risk_count = len(df_suppliers[df_suppliers['ESG_Score'] < 75])
    
    st.markdown("### Rekomendasi Operasional")
    
    col_op1, col_op2 = st.columns(2)
    with col_op1:
        st.markdown("**1. Rute Logistik & Cuaca**")
        if locked_logistics:
            ll = locked_logistics
            desiccant_text = f"Proteksi desiccant diwajibkan (Biaya: ${ll['desiccant_cost']:,.0f})." if ll['desiccant_cost'] > 0 else "Cuaca aman, proteksi tambahan tidak diperlukan."
            st.markdown(
                f"- **Rute Terpilih:** {ll['origin']} ➔ {ll['destination']} via {ll['mode_choice']}.\n"
                f"- **Waktu Tempuh:** {ll['lead_days']} hari perjalanan.\n"
                f"- **Mitigasi Lapangan:** {desiccant_text}"
            )
        else:
            st.markdown("- *Belum ada rute logistik yang dikunci.*")

    with col_op2:
        st.markdown("**2. Kesiapan Rantai Pasok (Vendor)**")
        if high_risk_count > 0:
            st.markdown(f"- **Risiko Vendor:** Ditemukan **{high_risk_count} vendor** dengan skor ESG di bawah batas aman (< 75).")
            st.markdown("- **Tindakan:** Wajib melakukan audit ISO/TKDN sebelum perpanjangan kontrak tahun depan untuk mencegah denda kepatuhan.")
        else:
            st.markdown("- Seluruh vendor berada di zona aman kepatuhan ESG.")
            st.markdown("- Lanjutkan skema prioritas Belanja Lokal (*Local Procurement*).")

    st.divider()

    # -------------------------------------------------------------------------
    # 4. BUKTI AUDIT (DI-PENDAM DI EXPANDER)
    # -------------------------------------------------------------------------
    with st.expander("📁 Bukti Data Audit & Log Sistem"):
        st.caption("File mentah dan log validasi Pydantic. Untuk keperluan audit internal.")
        
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            st.download_button("Unduh Data Emisi (CSV)", data=df_emissions.to_csv(index=False).encode('utf-8'), file_name=f"emissions_audit_{selected_year}.csv", mime="text/csv", use_container_width=True)
        with col_d2:
            st.download_button("Unduh Data Pemasok (CSV)", data=df_suppliers.to_csv(index=False).encode('utf-8'), file_name="suppliers_audit.csv", mime="text/csv", use_container_width=True)
        
        try:
            with open("logs/data_validation.log", "r", encoding="utf-8") as f:
                log_content = f.read()
            st.code(log_content, language="log")
        except Exception:
            st.warning("Log validasi tidak ditemukan.")

