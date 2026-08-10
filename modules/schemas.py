from pydantic import BaseModel, Field
from typing import Optional

from modules.constants import (
    ESG_BASE_WEIGHT,
    ISO14001_BONUS,
    TKDN_BONUS,
    CARBON_EFFICIENCY_THRESHOLD_HIGH,
    CARBON_EFFICIENCY_THRESHOLD_MEDIUM,
    CARBON_BONUS_HIGH,
    CARBON_BONUS_MEDIUM,
    LEAD_TIME_THRESHOLD_HIGH,
    LEAD_TIME_THRESHOLD_MEDIUM,
    LEAD_TIME_BONUS_HIGH,
    LEAD_TIME_BONUS_MEDIUM
)

class EmissionRecord(BaseModel):
    Year: int = Field(..., ge=2000, le=2100)
    Scope1_tCO2e: float = Field(default=0.0, ge=0)
    Scope2_tCO2e: float = Field(default=0.0, ge=0)
    Scope3_Cat4_UpstreamLogistics_tCO2e: float = Field(default=0.0, ge=0)
    Scope3_Cat6_BusinessTravel_tCO2e: float = Field(default=0.0, ge=0)
    Scope3_Cat1_PurchasedGoods_tCO2e: float = Field(default=0.0, ge=0)
    Revenue_MUSD: float = Field(default=0.0, ge=0)
    TKDN_Percentage: float = Field(default=0.0, ge=0, le=100)

class SupplierRecord(BaseModel):
    Supplier_ID: str
    Supplier_Name: str
    Category: str
    Spend_USD: float = Field(default=0.0, ge=0)
    ESG_Score: float = Field(default=0.0, ge=0, le=100)
    Location_Type: str = Field(default="Non-Local National")
    Carbon_Intensity_kgCO2_per_USD: float = Field(default=0.0, ge=0)
    Delivery_LeadTime_Days: int = Field(default=0, ge=0)
    TKDN_Compliant: str = Field(default="No")
    ISO14001_Certified: str = Field(default="No")

class RouteRecord(BaseModel):
    Route_ID: str
    Origin: str = Field(default="")
    Destination: str
    Lat_Dest: float
    Lon_Dest: float
    Distance_km: float = Field(default=1.0, ge=0)
    Transport_Mode: str = Field(default="")
    Avg_Monthly_Trips: int = Field(default=0, ge=0)
    Avg_Payload_Tons: float = Field(default=0.0, ge=0)
    Weather_Sensitivity: str = Field(default="Medium")

def calculate_dynamic_esg_score(base_esg: float, iso_certified: str, tkdn_compliant: str, carbon_intensity: float, lead_time_days: int) -> float:
    """
    Weighted ESG Scorecard Formula (GRI 308 / ISO 14001 Governance Standard):
    - Base Audit Score: 50% Weight
    - ISO 14001 Environmental Certification: +15 Points
    - TKDN Local Content Compliance: +15 Points
    - Carbon Efficiency Factor (<0.5 kgCO2/$): +10 Points
    - Lead Time Efficiency Factor (<14 Days): +10 Points
    """
    score = base_esg * ESG_BASE_WEIGHT
    if str(iso_certified).upper() in ["YES", "TRUE", "Y"]: score += ISO14001_BONUS
    if str(tkdn_compliant).upper() in ["YES", "TRUE", "Y"]: score += TKDN_BONUS
    if carbon_intensity <= CARBON_EFFICIENCY_THRESHOLD_HIGH: score += CARBON_BONUS_HIGH
    elif carbon_intensity <= CARBON_EFFICIENCY_THRESHOLD_MEDIUM: score += CARBON_BONUS_MEDIUM
    if lead_time_days <= LEAD_TIME_THRESHOLD_HIGH: score += LEAD_TIME_BONUS_HIGH
    elif lead_time_days <= LEAD_TIME_THRESHOLD_MEDIUM: score += LEAD_TIME_BONUS_MEDIUM
    return min(100.0, max(0.0, score))

