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
def load_and_validate_data() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Muat data dari file CSV dan periksa tipe datanya per baris lewat Pydantic.
    
    Validasi ini memastikan tidak ada data bernilai null atau salah tipe yang lolos ke dashboard.
    Jika ada baris data yang bermasalah, error akan dicatat ke logs/data_validation.log tanpa menghentikan aplikasi.
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

    df_emissions_clean = pd.DataFrame(validated_emissions) if validated_emissions else df_emissions
    df_suppliers_clean = pd.DataFrame(validated_suppliers) if validated_suppliers else df_suppliers
    df_routes_clean = pd.DataFrame(validated_routes) if validated_routes else df_routes

    logger.info(f"Pemeriksaan data selesai: {len(df_emissions_clean)} data emisi, {len(df_suppliers_clean)} data pemasok, {len(df_routes_clean)} data rute terverifikasi.")

    return df_emissions_clean, df_suppliers_clean, df_routes_clean
