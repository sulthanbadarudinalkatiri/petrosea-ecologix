"""
Centralized Scientific & Operational Constants for Petrosea EcoLogix
====================================================================
Every numerical assumption used in the application is registered here
with its source, confidence level, and unit — ensuring full model
transparency for auditors, reviewers, and the Board of Directors.

Primary References:
- IPCC 2019 Refinement to 2006 Guidelines for National GHG Inventories
- DEFRA / UK DESNZ 2024 Greenhouse Gas Reporting Conversion Factors
- PT Petrosea Tbk Net-Zero Corporate Target 2030 (30% Abatement)
- PT Petrosea Tbk Sustainability Report 2025
"""

# =============================================================================
# ASSUMPTION REGISTRY — Structured metadata for every model parameter
# =============================================================================
# Each entry: parameter, variable, value, unit, source, confidence, category, note
# Confidence: High = peer-reviewed / regulatory | Medium = industry benchmark | Low = prototype estimate

ASSUMPTION_REGISTRY = [
    # --- EMISSION ABATEMENT FACTORS ---
    {
        "parameter": "B100 Biodiesel Abatement Factor",
        "variable": "BIOFUEL_B100_ABATEMENT_FACTOR",
        "value": 0.18,
        "unit": "fraction (0–1)",
        "source": "IPCC 2019, Vol. 2, Ch. 3, Table 3.4.1",
        "confidence": "Medium",
        "category": "Emission Factor",
        "note": "Net lifecycle GHG reduction B100 vs fossil diesel (Scope 1)"
    },
    {
        "parameter": "EV Retrofit Abatement Factor",
        "variable": "EV_RETROFIT_ABATEMENT_FACTOR",
        "value": 0.25,
        "unit": "fraction (0–1)",
        "source": "Prototype estimate (OEM fleet electrification benchmark)",
        "confidence": "Low",
        "category": "Emission Factor",
        "note": "Scope 1 efficiency gain diesel-to-electric haul trucks"
    },
    {
        "parameter": "Local Procurement Logistics Abatement Factor",
        "variable": "LOCAL_PROC_LOGISTICS_ABATEMENT_FACTOR",
        "value": 0.35,
        "unit": "fraction (0–1)",
        "source": "Prototype estimate (supply chain proximity model)",
        "confidence": "Low",
        "category": "Emission Factor",
        "note": "Scope 3 Cat 1 & 4 reduction from local supply chain optimization"
    },
    {
        "parameter": "Barge Intermodal Shift Abatement Factor",
        "variable": "BARGE_INTERMODAL_SHIFT_ABATEMENT_FACTOR",
        "value": 0.38,
        "unit": "fraction (0–1)",
        "source": "DEFRA 2024 freight modal emission factors (barge vs truck)",
        "confidence": "Medium",
        "category": "Emission Factor",
        "note": "Scope 3 Cat 4 reduction from maritime barge vs road trucking"
    },
    # --- TRANSPORT EMISSION FACTORS PER TON-KM ---
    {
        "parameter": "Marine Barge Emission Factor",
        "variable": "EMISSION_FACTOR_BARGE_KG_PER_TKM",
        "value": 0.03,
        "unit": "kgCO2/ton-km",
        "source": "DEFRA 2024, Table 9 (Sea tanker, average)",
        "confidence": "High",
        "category": "Emission Factor",
        "note": "Coastal & inter-island barge freight"
    },
    {
        "parameter": "Trucking Emission Factor",
        "variable": "EMISSION_FACTOR_TRUCK_KG_PER_TKM",
        "value": 0.15,
        "unit": "kgCO2/ton-km",
        "source": "DEFRA 2024, Table 6 (HGV rigid, laden)",
        "confidence": "High",
        "category": "Emission Factor",
        "note": "Heavy goods vehicle road freight, Kalimantan corridors"
    },
    {
        "parameter": "Air Freight Emission Factor",
        "variable": "EMISSION_FACTOR_AIR_KG_PER_TKM",
        "value": 1.20,
        "unit": "kgCO2/ton-km",
        "source": "DEFRA 2024, Table 11 (Air freight, domestic)",
        "confidence": "High",
        "category": "Emission Factor",
        "note": "Emergency air freight for critical mining spareparts"
    },
    # --- MARGINAL ABATEMENT COST (MAC) COEFFICIENTS ---
    {
        "parameter": "MAC: Biofuel Substitution",
        "variable": "MC_BIOFUEL_USD_PER_TCO2E",
        "value": 14.0,
        "unit": "USD/tCO2e",
        "source": "Prototype estimate (biodiesel price premium model)",
        "confidence": "Low",
        "category": "Cost Coefficient",
        "note": "Net cost of biofuel substitution per ton CO2 abated"
    },
    {
        "parameter": "MAC: Local Procurement",
        "variable": "MC_LOCAL_PROCUREMENT_USD_PER_TCO2E",
        "value": -18.5,
        "unit": "USD/tCO2e",
        "source": "Prototype estimate (logistics cost saving model)",
        "confidence": "Low",
        "category": "Cost Coefficient",
        "note": "Negative = net savings from reduced transport distance"
    },
    {
        "parameter": "MAC: Barge Modal Shift",
        "variable": "MC_BARGE_MODAL_SHIFT_USD_PER_TCO2E",
        "value": -12.0,
        "unit": "USD/tCO2e",
        "source": "Prototype estimate (freight rate differential model)",
        "confidence": "Low",
        "category": "Cost Coefficient",
        "note": "Negative = net savings from cheaper barge vs truck rates"
    },
    {
        "parameter": "MAC: EV Fleet Retrofit",
        "variable": "MC_EV_RETROFIT_USD_PER_TCO2E",
        "value": 45.0,
        "unit": "USD/tCO2e",
        "source": "Prototype estimate (CAPEX/OPEX differential model)",
        "confidence": "Low",
        "category": "Cost Coefficient",
        "note": "Upfront cost premium for electric haul truck conversion"
    },
    # --- TRANSPORT OPERATIONAL PARAMETERS ---
    {
        "parameter": "Barge Speed",
        "variable": "BARGE_SPEED_KM_PER_DAY",
        "value": 120,
        "unit": "km/hari",
        "source": "Operational estimate (coastal barge, Kalimantan)",
        "confidence": "Medium",
        "category": "Operational",
        "note": "Average daily distance for inter-island barge freight"
    },
    {
        "parameter": "Truck Speed",
        "variable": "TRUCK_SPEED_KM_PER_DAY",
        "value": 350,
        "unit": "km/hari",
        "source": "Operational estimate (Kalimantan mining roads)",
        "confidence": "Medium",
        "category": "Operational",
        "note": "Average daily distance for heavy goods vehicle"
    },
    {
        "parameter": "Barge Loading Buffer",
        "variable": "BARGE_LOADING_BUFFER_DAYS",
        "value": 3,
        "unit": "hari",
        "source": "Operational estimate (port loading/unloading)",
        "confidence": "Medium",
        "category": "Operational",
        "note": "Additional days for port handling & scheduling"
    },
    {
        "parameter": "Truck Loading Buffer",
        "variable": "TRUCK_LOADING_BUFFER_DAYS",
        "value": 1,
        "unit": "hari",
        "source": "Operational estimate (warehouse dispatch)",
        "confidence": "Medium",
        "category": "Operational",
        "note": "Additional day for loading & dispatch"
    },
    {
        "parameter": "Desiccant Cost (Barge, Sealed Container)",
        "variable": "DESICCANT_COST_BARGE_USD",
        "value": 450.0,
        "unit": "USD",
        "source": "Prototype estimate (sealed container market price)",
        "confidence": "Low",
        "category": "Operational",
        "note": "Material protection for humidity-sensitive cargo via sea"
    },
    {
        "parameter": "Desiccant Cost (Truck, Standard)",
        "variable": "DESICCANT_COST_TRUCK_USD",
        "value": 250.0,
        "unit": "USD",
        "source": "Prototype estimate (standard desiccant market price)",
        "confidence": "Low",
        "category": "Operational",
        "note": "Material protection for humidity-sensitive cargo via road"
    },
    {
        "parameter": "Humidity Threshold for Desiccant",
        "variable": "HUMIDITY_THRESHOLD_DESICCANT_PCT",
        "value": 80,
        "unit": "% RH",
        "source": "Material protection guideline (general industry)",
        "confidence": "Medium",
        "category": "Operational",
        "note": "Above this threshold, desiccant protection is recommended"
    },
    {
        "parameter": "Default Payload (Fallback)",
        "variable": "DEFAULT_PAYLOAD_TONS",
        "value": 50.0,
        "unit": "metric tons",
        "source": "Fallback default (used only when route data unavailable)",
        "confidence": "Medium",
        "category": "Operational",
        "note": "Replaced by actual Avg_Payload_Tons from route CSV when available"
    },
    # --- CORPORATE TARGETS & GOVERNANCE ---
    {
        "parameter": "Net-Zero Target 2030",
        "variable": "NET_ZERO_TARGET_PERCENTAGE",
        "value": 30.0,
        "unit": "% reduction",
        "source": "PT Petrosea Tbk Corporate Strategy 2030",
        "confidence": "High",
        "category": "Governance",
        "note": "Official corporate abatement target"
    },
    {
        "parameter": "Default Carbon Price",
        "variable": "DEFAULT_CARBON_PRICE_USD",
        "value": 25.0,
        "unit": "USD/tCO2e",
        "source": "Prototype estimate (above Indonesia Law No. 7/2021 floor of ~$1.90)",
        "confidence": "Low",
        "category": "Governance",
        "note": "Adjustable via UI slider. Indonesia carbon tax floor: IDR 30,000/tCO2e"
    },
    {
        "parameter": "ESG High-Risk Threshold",
        "variable": "ESG_HIGH_RISK_THRESHOLD",
        "value": 75.0,
        "unit": "score (0–100)",
        "source": "Petrosea internal governance standard",
        "confidence": "Medium",
        "category": "Governance",
        "note": "Suppliers scoring below 75 require priority audit"
    },
    {
        "parameter": "Max Benchmark Lead Time",
        "variable": "MAX_BENCHMARK_LEAD_TIME_DAYS",
        "value": 60,
        "unit": "hari",
        "source": "Industry benchmark (mining supply chain)",
        "confidence": "Medium",
        "category": "Governance",
        "note": "Maximum expected supply chain lead time"
    },
    {
        "parameter": "Max Benchmark Carbon Intensity",
        "variable": "MAX_BENCHMARK_CARBON_INTENSITY",
        "value": 1.0,
        "unit": "kgCO2/USD",
        "source": "Industry benchmark (vendor carbon efficiency)",
        "confidence": "Medium",
        "category": "Governance",
        "note": "Baseline maximum acceptable vendor carbon intensity"
    },
    # --- ENVIRONMENTAL EQUIVALENCY CONVERSIONS ---
    {
        "parameter": "Trees Planted per tCO2e",
        "variable": "TREES_PLANTED_PER_TON_CO2",
        "value": 45.45,
        "unit": "pohon/tCO2e",
        "source": "IPCC tropical forest sequestration (~22 kgCO2/tree/yr)",
        "confidence": "Medium",
        "category": "Equivalency",
        "note": "Mature Borneo rainforest trees absorbing CO2 annually"
    },
    {
        "parameter": "Diesel Trucks Retired per tCO2e",
        "variable": "DIESEL_TRUCKS_RETIRED_PER_TON_CO2",
        "value": 0.217,
        "unit": "truk/tCO2e",
        "source": "Prototype estimate (simplified conversion)",
        "confidence": "Low",
        "category": "Equivalency",
        "note": "Approximate heavy mining haul truck equivalent"
    },
    {
        "parameter": "Homes Powered per tCO2e",
        "variable": "HOMES_POWERED_PER_TON_CO2",
        "value": 0.125,
        "unit": "rumah/tCO2e",
        "source": "Prototype estimate (US EPA benchmark, not Indonesia-adjusted)",
        "confidence": "Low",
        "category": "Equivalency",
        "note": "Households powered by clean energy equivalent"
    },
    # --- SCOPE 3 EMISSION CATEGORY ALLOCATIONS ---
    {
        "parameter": "Scope 3 Cat 4 Allocation (2023-2024)",
        "variable": "SCOPE3_2023_24_CAT4_ALLOCATION",
        "value": 0.70,
        "unit": "ratio",
        "source": "Derived Assumption",
        "confidence": "Low",
        "category": "Sustainability",
        "note": "Upstream Logistics allocation before 2025 refinement"
    },
    {
        "parameter": "Scope 3 Cat 6 Allocation (2023-2024)",
        "variable": "SCOPE3_2023_24_CAT6_ALLOCATION",
        "value": 0.10,
        "unit": "ratio",
        "source": "Derived Assumption",
        "confidence": "Low",
        "category": "Sustainability",
        "note": "Business Travel allocation before 2025 refinement"
    },
    {
        "parameter": "Scope 3 Cat 1 Allocation (2023-2024)",
        "variable": "SCOPE3_2023_24_CAT1_ALLOCATION",
        "value": 0.20,
        "unit": "ratio",
        "source": "Derived Assumption",
        "confidence": "Low",
        "category": "Sustainability",
        "note": "Purchased Goods allocation before 2025 refinement"
    },
    {
        "parameter": "Scope 3 Cat 4 Allocation (2025)",
        "variable": "SCOPE3_2025_CAT4_ALLOCATION",
        "value": 0.186,
        "unit": "ratio",
        "source": "Model Reconstruction",
        "confidence": "Medium",
        "category": "Sustainability",
        "note": "Refined Upstream Logistics allocation from 2025 PDF disclosures"
    },
    {
        "parameter": "Scope 3 Cat 6 Allocation (2025)",
        "variable": "SCOPE3_2025_CAT6_ALLOCATION",
        "value": 0.0105,
        "unit": "ratio",
        "source": "Model Reconstruction",
        "confidence": "Medium",
        "category": "Sustainability",
        "note": "Refined Business Travel allocation from 2025 PDF disclosures"
    },
    {
        "parameter": "Scope 3 Cat 1 Allocation (2025)",
        "variable": "SCOPE3_2025_CAT1_ALLOCATION",
        "value": 0.8035,
        "unit": "ratio",
        "source": "Model Reconstruction",
        "confidence": "Medium",
        "category": "Sustainability",
        "note": "Refined Purchased Goods allocation from 2025 PDF disclosures"
    },
]

# =============================================================================
# NAMED CONSTANTS — Top-level variables for backward compatibility
# =============================================================================
# These are auto-derived from ASSUMPTION_REGISTRY so every import still works.

def _build_constants():
    """Extract named constants from the registry into module-level variables."""
    g = globals()
    for entry in ASSUMPTION_REGISTRY:
        g[entry["variable"]] = entry["value"]

_build_constants()
