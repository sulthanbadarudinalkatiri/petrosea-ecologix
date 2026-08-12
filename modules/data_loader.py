import streamlit as st
import pandas as pd
import logging
import os
from typing import Tuple, List
import pathlib
from modules.schemas import EmissionRecord, SupplierRecord, RouteRecord

# Menyiapkan folder dan file log untuk mencatat hasil validasi data
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename="logs/data_validation.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

@st.cache_data
def _load_and_validate_data_cached(mtime_e: float, mtime_s: float, mtime_r: float) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Muat data dari file CSV dan periksa tipe datanya per baris lewat Pydantic.
    (Di-cache berdasarkan timestamp modifikasi file untuk mencegah log spam saat UI render)
    """
    base_path = pathlib.Path(__file__).parent.parent / "data"
    df_emissions = pd.read_csv(base_path / "emissions.csv")
    df_suppliers = pd.read_csv(base_path / "suppliers.csv")
    df_routes = pd.read_csv(base_path / "rute_logistik.csv")

    validated_emissions: List[dict] = []
    for idx, row in enumerate(df_emissions.to_dict(orient="records")):
        try:
            record = EmissionRecord(**row)
            validated_emissions.append(record.model_dump())
        except Exception as e:
            logger.error(f"Data emisi tidak valid [Baris {idx+1}]: {e}")

    validated_suppliers: List[dict] = []
    for idx, row in enumerate(df_suppliers.to_dict(orient="records")):
        try:
            record = SupplierRecord(**row)
            validated_suppliers.append(record.model_dump())
        except Exception as e:
            logger.error(f"Data pemasok tidak valid [Baris {idx+1}]: {e}")

    validated_routes: List[dict] = []
    for idx, row in enumerate(df_routes.to_dict(orient="records")):
        try:
            record = RouteRecord(**row)
            validated_routes.append(record.model_dump())
        except Exception as e:
            logger.error(f"Data rute logistik tidak valid [Baris {idx+1}]: {e}")

    if not validated_emissions:
        raise ValueError("FATAL ERROR: Validasi data emisi gagal total. File emissions.csv korup atau format tidak sesuai schema. Sistem ESG dihentikan.")
    if not validated_suppliers:
        raise ValueError("FATAL ERROR: Validasi data pemasok gagal total. File suppliers.csv korup atau format tidak sesuai schema. Sistem ESG dihentikan.")
    if not validated_routes:
        raise ValueError("FATAL ERROR: Validasi data rute logistik gagal total. File rute_logistik.csv korup atau format tidak sesuai schema. Sistem ESG dihentikan.")

    df_emissions_clean = pd.DataFrame(validated_emissions)
    df_suppliers_clean = pd.DataFrame(validated_suppliers)
    df_routes_clean = pd.DataFrame(validated_routes)

    logger.info(f"Pemeriksaan data selesai: {len(df_emissions_clean)} data emisi, {len(df_suppliers_clean)} data pemasok, {len(df_routes_clean)} data rute terverifikasi.")

    return df_emissions_clean, df_suppliers_clean, df_routes_clean

def load_and_validate_data() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Fungsi wrapper untuk mendeteksi perubahan file. Jika file CSV di-update, 
    mtime akan berubah, membongkar cache, memicu validasi ulang, dan mencatat log audit baru.
    """
    base_path = pathlib.Path(__file__).parent.parent / "data"
    f_e = base_path / "emissions.csv"
    f_s = base_path / "suppliers.csv"
    f_r = base_path / "rute_logistik.csv"

    mtime_e = os.path.getmtime(f_e) if f_e.exists() else 0
    mtime_s = os.path.getmtime(f_s) if f_s.exists() else 0
    mtime_r = os.path.getmtime(f_r) if f_r.exists() else 0

    return _load_and_validate_data_cached(mtime_e, mtime_s, mtime_r)
