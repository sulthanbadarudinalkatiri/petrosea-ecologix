# Petrosea EcoLogix — Dashboard Dekarbonisasi Logistik & Supply Chain
[![Streamlit](https://img.shields.io/badge/Streamlit-1.42.0-FF4B4B?logo=streamlit)](https://streamlit.io/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python)](https://python.org)
[![SciPy](https://img.shields.io/badge/SciPy-Optimization-8CAAE6?logo=scipy)](https://scipy.org)
[![Pydantic](https://img.shields.io/badge/Pydantic-v2-E92063?logo=pydantic)](https://pydantic.dev/)
[![Plotly](https://img.shields.io/badge/Plotly-Express-3F4F75?logo=plotly)](https://plotly.com/)

## Ringkasan Proyek
Dashboard berbasis Streamlit untuk menganalisis data emisi dan rantai pasok dari Laporan Keberlanjutan PT Petrosea Tbk 2025. Aplikasi ini mengekstrak data PDF, memvalidasinya dengan Pydantic, memetakan risiko vendor, membandingkan moda transportasi (Barge vs Truk vs Udara), dan menghitung skenario penghematan karbon termurah menggunakan SciPy Linear Programming.

Aplikasi dibagi menjadi tiga modul:

*   **Diagnosis Emisi & Risiko Pemasok**: Tren emisi historis dan evaluasi kepatuhan vendor (ESG/TKDN/ISO 14001).
*   **Simulator Logistik & Kebijakan Karbon**: Peta cuaca real-time, perbandingan moda angkut, dan solver optimasi linier.
*   **Ringkasan Eksekutif**: Rekap keputusan dinamis, perhitungan eksposur pajak karbon, dan log audit.

## Filosofi Desain & Batasan Data
Dashboard ini dirancang mengikuti pembagian standar GHG Protocol berdasarkan ketersediaan data publik:

*   **Modul Diagnosis (Tab 1)**: Berfokus pada Scope 3 Category 1 (Purchased Goods). Data diekstrak dari laporan keuangan/vendor publik. Di sini, penilaian risiko dilakukan berdasarkan kualitas vendor (ESG/ISO), bukan berdasarkan jalur pengiriman.
*   **Modul Simulator (Tab 2)**: Berfokus pada Scope 3 Category 4 (Upstream Transportation). Karena laporan publik tidak pernah mencantumkan pemetaan rute spesifik per vendor (alasan keamanan operasional), simulator logistik ini berdiri sebagai alat bantu evaluasi moda transportasi umum.
*   **Mengapa tidak digabung?** Menghubungkan "Vendor A" secara langsung ke "Rute B" memerlukan data internal (mapping vendor-rute) yang bersifat proprietary. Oleh karena itu, aplikasi ini berfungsi sebagai Decision Support System terpisah yang memfasilitasi diskusi lintas departemen (Procurement vs Logistics), bukan sistem end-to-end otomatis.

## Fitur Utama
### 1. Tema UI Adaptif
Menggunakan variabel CSS bawaan Streamlit (`var(--background-color)`, `var(--text-color)`) dengan palet warna Teal (`#005A36`) dan Oranye (`#E87722`). UI aman dan otomatis menyesuaikan saat pengguna berpindah antara Light Mode dan Dark Mode tanpa perlu menambahkan `@media` query manual.

### 2. Parallel API Engine
Menggunakan `concurrent.futures.ThreadPoolExecutor` (10 workers) untuk mengambil data cuaca dan indeks kualitas udara (US AQI) dari Open-Meteo API secara paralel. Waktu muat aplikasi berkurang dari ~15 detik (sekuensial) menjadi ~1.5 detik, dengan cache `@st.cache_data(ttl=3600)`.

### 3. Optimasi Biaya Karbon (SciPy linprog)
Menggunakan solver HiGHS untuk menghitung alokasi 4 variabel dekarbonisasi (Biofuel, Belanja Lokal, Moda Barge, EV Fleet) dengan biaya serendah mungkin, tetap memenuhi batasan emisi (misal: target 30%). Dilengkapi tombol preset cepat.

### 4. Ringkasan Eksekutif Dinamis (Tab 3)
Status laporan berubah secara otomatis berdasarkan input pengguna: `○ DRAFT` (kalo belum ada simulasi) atau `● FINAL` (kalo skenario udah dikunci dari Tab 2). Menampilkan perbandingan eksposur pajak karbon (Do-Nothing vs Skenario Mitigasi).

### 5. Registri Asumsi Model (Assumption Registry)
Seluruh koefisien emisi dan biaya marginal (MAC) didokumentasikan dalam satu file (`constants.py`) lengkap dengan sumber referensi (IPCC, DEFRA 2024) dan tingkat keyakinan (High/Medium/Low). Tabel ini bisa di-export langsung ke CSV dari dalam dashboard untuk keperluan audit.

## Tampilan Modul Dashboard
*   **Tab 1: Profil Emisi & Risiko Pemasok**
    *   Grafik batang dan garis (Plotly) untuk tren Scope 1, 2, 3, dan intensitas karbon per pendapatan.
    *   Scatter plot (Spend vs ESG Score) dan Radar Chart untuk menilai kepatuhan vendor.
*   **Tab 2: Simulator Logistik & Optimasi Karbon**
    *   Peta interaktif Folium dengan marker warna berdasarkan status cuaca real-time.
    *   Matriks perbandingan 3 moda angkut (Waktu, Emisi, Biaya Proteksi Desiccant).
    *   Slider kebijakan & solver otomatis untuk proyeksi penghematan biaya.
*   **Tab 3: Ringkasan Eksekutif & Audit**
    *   Kartu perbandingan pajak karbon (Baseline vs Pasca-Mitigasi).
    *   Poin-poin rekomendasi rute dan kesiapan vendor.
    *   Expander tersembunyi berisi file CSV mentah dan log validasi Pydantic.
## Filosofi Desain & Batasan Data
Dashboard ini dirancang mengikuti pembagian standar GHG Protocol berdasarkan ketersediaan data publik:

Modul Diagnosis (Tab 1): Berfokus pada Scope 3 Category 1 (Purchased Goods). Data diekstrak dari laporan keuangan/vendor publik. Di sini, penilaian risiko dilakukan berdasarkan kualitas vendor (ESG/ISO), bukan berdasarkan jalur pengiriman.

Modul Simulator (Tab 2): Berfokus pada Scope 3 Category 4 (Upstream Transportation). Karena laporan publik tidak pernah mencantumkan pemetaan rute spesifik per vendor (alasan keamanan operasional), simulator logistik ini berdiri sebagai alat bantu evaluasi moda transportasi umum.

Mengapa tidak digabung? Menghubungkan "Vendor A" secara langsung ke "Rute B" memerlukan data internal (mapping vendor-rute) yang bersifat proprietary. Oleh karena itu, aplikasi ini berfungsi sebagai Decision Support System terpisah yang memfasilitasi diskusi lintas departemen (Procurement vs Logistics), bukan sistem end-to-end otomatis.

## Alur Kerja Data & Arsitektur Sistem

<img width="1362" height="768" alt="workflow" src="https://github.com/user-attachments/assets/9d8a220b-85c4-4915-a3ca-c6e2103e3222" />

### Lifecycle Data (Data Flow)
1. **Ingestion & Validation**: Saat aplikasi dimuat, `data_loader.py` membaca dataset statis dan memaksakan validasi tipe menggunakan **Pydantic** (`schemas.py`). Ini memastikan *fail-safe* (jika data rusak, aplikasi menolak *render*).
2. **Real-time Enrichment**: Di Modul Tab 2, sistem melakukan *fetch* paralel ke **Open-Meteo API** (via `ThreadPoolExecutor` dengan 10 *workers* dan *timeout* 5 detik) untuk memperkaya data rute statis dengan parameter cuaca & AQI aktual.
3. **Event Engine & Tolerance Window**: Data cuaca dievaluasi. Jika curah hujan > 20 mm atau AQI > 150, sistem menyalakan *severity warning* untuk rute tersebut menggunakan pola *Progressive Disclosure*.
4. **Optimization (SciPy Linprog)**: User menggeser *slider* target pengurangan emisi. Sistem memanggil *solver* **HiGHS** dari SciPy. Fungsi tujuan (Z) adalah meminimalkan biaya tambahan (*Marginal Abatement Cost*) sambil memenuhi batasan (target % reduksi & batas maksimal per intervensi).
5. **State Persistance**: Hasil optimasi dikunci dan disimpan dalam memori (`st.session_state['locked_decarb']`).
6. **Executive Briefing**: Tab 3 membaca sesi tersebut dan menghitung **Carbon Tax Exposure** secara dinamis (Emisi Sisa × $2.00 Tarif Pajak Karbon Dasar) untuk memberikan ringkasan yang *decision-ready*.

## Stack Teknologi
*   **Framework**: Python 3.10+, Streamlit 1.42.0
*   **Optimization**: SciPy (`scipy.optimize.linprog`)
*   **Concurrency**: `concurrent.futures.ThreadPoolExecutor`
*   **Data Validation**: Pandas, Pydantic v2
*   **PDF Extraction**: PyMuPDF (fitz), Regex
*   **Visuals & Maps**: Plotly, Folium, Open-Meteo API

## Cara Menjalankan di Lokal
### 1. Clone Repositori
```bash
git clone https://github.com/sulthanbadarudinalkatiri/petrosea-ecologix.git
cd petrosea-ecologix
```

### 2. Install Pustaka
```bash
python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate # Linux/macOS

pip install -r requirements.txt
```

### 3. Jalankan Aplikasi
```bash
streamlit run app.py
```

---
**Pengembang**
Sulthan Badarudin Al-Katiri
Proyek Portofolio: Petrosea EcoLogix — ESG & Supply Chain Decarbonization Platform
