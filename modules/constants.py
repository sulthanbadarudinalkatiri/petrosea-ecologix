"""
Centralized Scientific & Operational Constants for Petrosea EcoLogix
====================================================================
Core model parameters are registered here
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
# Evidence Level: High = peer-reviewed / regulatory | Medium = industry benchmark | Low = prototype estimate

ASSUMPTION_REGISTRY = [
    # --- EMISSION ABATEMENT FACTORS ---
    {
        "parameter": "B100 Biodiesel Abatement Factor",
        "variable": "BIOFUEL_B100_ABATEMENT_FACTOR",
        "value": 0.18,
        "unit": "fraction (0–1)",
        "source": "IPCC 2019, Vol. 2, Ch. 3, Table 3.4.1",
        "evidence_level": "Medium",
        "category": "Emission Factor",
        "type": "REPORTED",
        "note": "Net lifecycle GHG reduction B100 vs fossil diesel (Scope 1)"
    },
    {
        "parameter": "EV Retrofit Abatement Factor",
        "variable": "EV_RETROFIT_ABATEMENT_FACTOR",
        "value": 0.25,
        "unit": "fraction (0–1)",
        "source": "Prototype estimate (OEM fleet electrification benchmark)",
        "evidence_level": "Low",
        "category": "Emission Factor",
        "type": "REPORTED",
        "note": "Scope 1 efficiency gain diesel-to-electric haul trucks"
    },
    {
        "parameter": "Local Procurement Logistics Abatement Factor",
        "variable": "LOCAL_PROC_LOGISTICS_ABATEMENT_FACTOR",
        "value": 0.35,
        "unit": "fraction (0–1)",
        "source": "Prototype estimate (supply chain proximity model)",
        "evidence_level": "Low",
        "category": "Emission Factor",
        "type": "REPORTED",
        "note": "Scope 3 Cat 1 & 4 reduction from local supply chain optimization"
    },
    {
        "parameter": "Barge Intermodal Shift Abatement Factor",
        "variable": "BARGE_INTERMODAL_SHIFT_ABATEMENT_FACTOR",
        "value": 0.38,
        "unit": "fraction (0–1)",
        "source": "DEFRA 2024 freight modal emission factors (barge vs truck)",
        "evidence_level": "Medium",
        "category": "Emission Factor",
        "type": "REPORTED",
        "note": "Scope 3 Cat 4 reduction from maritime barge vs road trucking"
    },
    # --- TRANSPORT EMISSION FACTORS PER TON-KM ---
    {
        "parameter": "Marine Barge Emission Factor",
        "variable": "EMISSION_FACTOR_BARGE_KG_PER_TKM",
        "value": 0.03,
        "unit": "kgCO2/ton-km",
        "source": "DEFRA 2024, Table 9 (Sea tanker, average)",
        "evidence_level": "High",
        "category": "Emission Factor",
        "type": "REPORTED",
        "note": "Coastal & inter-island barge freight"
    },
    {
        "parameter": "Trucking Emission Factor",
        "variable": "EMISSION_FACTOR_TRUCK_KG_PER_TKM",
        "value": 0.15,
        "unit": "kgCO2/ton-km",
        "source": "DEFRA 2024, Table 6 (HGV rigid, laden)",
        "evidence_level": "High",
        "category": "Emission Factor",
        "type": "REPORTED",
        "note": "Heavy goods vehicle road freight, Kalimantan corridors"
    },
    {
        "parameter": "Air Freight Emission Factor",
        "variable": "EMISSION_FACTOR_AIR_KG_PER_TKM",
        "value": 1.20,
        "unit": "kgCO2/ton-km",
        "source": "DEFRA 2024, Table 11 (Air freight, domestic)",
        "evidence_level": "High",
        "category": "Emission Factor",
        "type": "REPORTED",
        "note": "Emergency air freight for critical mining spareparts"
    },
    # --- MARGINAL ABATEMENT COST (MAC) COEFFICIENTS ---
    {
        "parameter": "MAC: Biofuel Substitution",
        "variable": "MC_BIOFUEL_USD_PER_TCO2E",
        "value": 14.0,
        "unit": "USD/tCO2e",
        "source": "Prototype estimate (biodiesel price premium model)",
        "evidence_level": "Low",
        "category": "Cost Coefficient",
        "type": "ASSUMPTION",
        "note": "Net cost of biofuel substitution per ton CO2 abated"
    },
    {
        "parameter": "MAC: Local Procurement",
        "variable": "MC_LOCAL_PROCUREMENT_USD_PER_TCO2E",
        "value": -18.5,
        "unit": "USD/tCO2e",
        "source": "Prototype estimate (logistics cost saving model)",
        "evidence_level": "Low",
        "category": "Cost Coefficient",
        "type": "ASSUMPTION",
        "note": "Negative = net savings from reduced transport distance"
    },
    {
        "parameter": "MAC: Barge Modal Shift",
        "variable": "MC_BARGE_MODAL_SHIFT_USD_PER_TCO2E",
        "value": -12.0,
        "unit": "USD/tCO2e",
        "source": "Prototype estimate (freight rate differential model)",
        "evidence_level": "Low",
        "category": "Cost Coefficient",
        "type": "ASSUMPTION",
        "note": "Negative = net savings from cheaper barge vs truck rates"
    },
    {
        "parameter": "MAC: EV Fleet Retrofit",
        "variable": "MC_EV_RETROFIT_USD_PER_TCO2E",
        "value": 45.0,
        "unit": "USD/tCO2e",
        "source": "Prototype estimate (CAPEX/OPEX differential model)",
        "evidence_level": "Low",
        "category": "Cost Coefficient",
        "type": "ASSUMPTION",
        "note": "Upfront cost premium for electric haul truck conversion"
    },
    # --- TRANSPORT OPERATIONAL PARAMETERS ---
    {
        "parameter": "Barge Speed",
        "variable": "BARGE_SPEED_KM_PER_DAY",
        "value": 120,
        "unit": "km/hari",
        "source": "Operational estimate (coastal barge, Kalimantan)",
        "evidence_level": "Medium",
        "category": "Operational",
        "type": "MODEL_PARAMETER",
        "note": "Average daily distance for inter-island barge freight"
    },
    {
        "parameter": "Truck Speed",
        "variable": "TRUCK_SPEED_KM_PER_DAY",
        "value": 350,
        "unit": "km/hari",
        "source": "Operational estimate (Kalimantan mining roads)",
        "evidence_level": "Medium",
        "category": "Operational",
        "type": "MODEL_PARAMETER",
        "note": "Average daily distance for heavy goods vehicle"
    },
    {
        "parameter": "Barge Loading Buffer",
        "variable": "BARGE_LOADING_BUFFER_DAYS",
        "value": 3,
        "unit": "hari",
        "source": "Operational estimate (port loading/unloading)",
        "evidence_level": "Medium",
        "category": "Operational",
        "type": "MODEL_PARAMETER",
        "note": "Additional days for port handling & scheduling"
    },
    {
        "parameter": "Truck Loading Buffer",
        "variable": "TRUCK_LOADING_BUFFER_DAYS",
        "value": 1,
        "unit": "hari",
        "source": "Operational estimate (warehouse dispatch)",
        "evidence_level": "Medium",
        "category": "Operational",
        "type": "MODEL_PARAMETER",
        "note": "Additional day for loading & dispatch"
    },
    {
        "parameter": "Desiccant Cost (Barge, Sealed Container)",
        "variable": "DESICCANT_COST_BARGE_USD",
        "value": 450.0,
        "unit": "USD",
        "source": "Prototype estimate (sealed container market price)",
        "evidence_level": "Low",
        "category": "Operational",
        "type": "MODEL_PARAMETER",
        "note": "Material protection for humidity-sensitive cargo via sea"
    },
    {
        "parameter": "Desiccant Cost (Truck, Standard)",
        "variable": "DESICCANT_COST_TRUCK_USD",
        "value": 250.0,
        "unit": "USD",
        "source": "Prototype estimate (standard desiccant market price)",
        "evidence_level": "Low",
        "category": "Operational",
        "type": "MODEL_PARAMETER",
        "note": "Material protection for humidity-sensitive cargo via road"
    },
    {
        "parameter": "Humidity Threshold for Desiccant",
        "variable": "HUMIDITY_THRESHOLD_DESICCANT_PCT",
        "value": 80,
        "unit": "% RH",
        "source": "Material protection guideline (general industry)",
        "evidence_level": "Medium",
        "category": "Operational",
        "type": "MODEL_PARAMETER",
        "note": "Above this threshold, desiccant protection is recommended"
    },
    {
        "parameter": "Default Payload (Fallback)",
        "variable": "DEFAULT_PAYLOAD_TONS",
        "value": 50.0,
        "unit": "metric tons",
        "source": "Fallback default (used only when route data unavailable)",
        "evidence_level": "Medium",
        "category": "Operational",
        "type": "MODEL_PARAMETER",
        "note": "Replaced by actual Avg_Payload_Tons from route CSV when available"
    },
    # --- CORPORATE TARGETS & GOVERNANCE ---
    {
        "parameter": "Net-Zero Target 2030",
        "variable": "NET_ZERO_TARGET_PERCENTAGE",
        "value": 30.0,
        "unit": "% reduction",
        "source": "PT Petrosea Tbk Corporate Strategy 2030",
        "evidence_level": "High",
        "category": "Governance",
        "type": "ASSUMPTION",
        "note": "Official corporate abatement target"
    },
    {
        "parameter": "Default Carbon Price",
        "variable": "DEFAULT_CARBON_PRICE_USD",
        "value": 25.0,
        "unit": "USD/tCO2e",
        "source": "Prototype estimate (above Indonesia Law No. 7/2021 floor of ~$1.90)",
        "evidence_level": "Low",
        "category": "Governance",
        "type": "ASSUMPTION",
        "note": "Adjustable via UI slider. Indonesia carbon tax floor: IDR 30,000/tCO2e"
    },
    {
        "parameter": "ESG High-Risk Threshold",
        "variable": "ESG_HIGH_RISK_THRESHOLD",
        "value": 75.0,
        "unit": "score (0–100)",
        "source": "Petrosea internal governance standard",
        "evidence_level": "Medium",
        "category": "Governance",
        "type": "ASSUMPTION",
        "note": "Suppliers scoring below 75 require priority audit"
    },
    {
        "parameter": "Max Benchmark Lead Time",
        "variable": "MAX_BENCHMARK_LEAD_TIME_DAYS",
        "value": 60,
        "unit": "hari",
        "source": "Industry benchmark (mining supply chain)",
        "evidence_level": "Medium",
        "category": "Governance",
        "type": "ASSUMPTION",
        "note": "Maximum expected supply chain lead time"
    },
    {
        "parameter": "Max Benchmark Carbon Intensity",
        "variable": "MAX_BENCHMARK_CARBON_INTENSITY",
        "value": 1.0,
        "unit": "kgCO2/USD",
        "source": "Industry benchmark (vendor carbon efficiency)",
        "evidence_level": "Medium",
        "category": "Governance",
        "type": "ASSUMPTION",
        "note": "Baseline maximum acceptable vendor carbon intensity"
    },
    # --- ENVIRONMENTAL EQUIVALENCY CONVERSIONS ---
    {
        "parameter": "Trees Planted per tCO2e",
        "variable": "TREES_PLANTED_PER_TON_CO2",
        "value": 45.45,
        "unit": "pohon/tCO2e",
        "source": "IPCC tropical forest sequestration (~22 kgCO2/tree/yr)",
        "evidence_level": "Medium",
        "category": "Equivalency",
        "type": "DERIVED",
        "note": "Mature Borneo rainforest trees absorbing CO2 annually"
    },
    {
        "parameter": "Diesel Trucks Retired per tCO2e",
        "variable": "DIESEL_TRUCKS_RETIRED_PER_TON_CO2",
        "value": 0.217,
        "unit": "truk/tCO2e",
        "source": "Prototype estimate (simplified conversion)",
        "evidence_level": "Low",
        "category": "Equivalency",
        "type": "DERIVED",
        "note": "Approximate heavy mining haul truck equivalent"
    },
    {
        "parameter": "Homes Powered per tCO2e",
        "variable": "HOMES_POWERED_PER_TON_CO2",
        "value": 0.125,
        "unit": "rumah/tCO2e",
        "source": "Prototype estimate (US EPA benchmark, not Indonesia-adjusted)",
        "evidence_level": "Low",
        "category": "Equivalency",
        "type": "DERIVED",
        "note": "Households powered by clean energy equivalent"
    },
    # --- SCOPE 3 EMISSION CATEGORY ALLOCATIONS ---
    {
        "parameter": "Scope 3 Cat 4 Allocation (2023-2024)",
        "variable": "SCOPE3_2023_24_CAT4_ALLOCATION",
        "value": 0.70,
        "unit": "ratio",
        "source": "Derived Assumption",
        "evidence_level": "Low",
        "category": "Sustainability",
        "type": "ASSUMPTION",
        "note": "Upstream Logistics allocation before 2025 refinement"
    },
    {
        "parameter": "Scope 3 Cat 6 Allocation (2023-2024)",
        "variable": "SCOPE3_2023_24_CAT6_ALLOCATION",
        "value": 0.10,
        "unit": "ratio",
        "source": "Derived Assumption",
        "evidence_level": "Low",
        "category": "Sustainability",
        "type": "ASSUMPTION",
        "note": "Business Travel allocation before 2025 refinement"
    },
    {
        "parameter": "Scope 3 Cat 1 Allocation (2023-2024)",
        "variable": "SCOPE3_2023_24_CAT1_ALLOCATION",
        "value": 0.20,
        "unit": "ratio",
        "source": "Derived Assumption",
        "evidence_level": "Low",
        "category": "Sustainability",
        "type": "ASSUMPTION",
        "note": "Purchased Goods allocation before 2025 refinement"
    },
    {
        "parameter": "Scope 3 Cat 4 Allocation (2025)",
        "variable": "SCOPE3_2025_CAT4_ALLOCATION",
        "value": 0.186,
        "unit": "ratio",
        "source": "Model Reconstruction",
        "evidence_level": "Medium",
        "category": "Sustainability",
        "type": "ASSUMPTION",
        "note": "Refined Upstream Logistics allocation from 2025 PDF disclosures"
    },
    {
        "parameter": "Scope 3 Cat 6 Allocation (2025)",
        "variable": "SCOPE3_2025_CAT6_ALLOCATION",
        "value": 0.0105,
        "unit": "ratio",
        "source": "Model Reconstruction",
        "evidence_level": "Medium",
        "category": "Sustainability",
        "type": "ASSUMPTION",
        "note": "Refined Business Travel allocation from 2025 PDF disclosures"
    },
    {
        "parameter": "Scope 3 Cat 1 Allocation (2025)",
        "variable": "SCOPE3_2025_CAT1_ALLOCATION",
        "value": 0.8035,
        "unit": "ratio",
        "source": "Model Reconstruction",
        "evidence_level": "Medium",
        "category": "Sustainability",
        "type": "ASSUMPTION",
        "note": "Refined Purchased Goods allocation from 2025 PDF disclosures"
    },
    # --- DYNAMIC ESG SCORING PARAMETERS ---
    {
        "parameter": "Base ESG Weight",
        "variable": "ESG_BASE_WEIGHT",
        "value": 0.50,
        "unit": "fraction (0-1)",
        "source": "Model Reconstruction (GRI 308 standard weighting)",
        "evidence_level": "Medium",
        "category": "Risk Factor",
        "type": "MODEL_PARAMETER",
        "note": "Weight applied to base audit score"
    },
    {
        "parameter": "ISO 14001 Bonus",
        "variable": "ISO14001_BONUS",
        "value": 15.0,
        "unit": "points",
        "source": "Model Reconstruction",
        "evidence_level": "Low",
        "category": "Risk Factor",
        "type": "MODEL_PARAMETER",
        "note": "Bonus points for environmental certification"
    },
    {
        "parameter": "TKDN Bonus",
        "variable": "TKDN_BONUS",
        "value": 15.0,
        "unit": "points",
        "source": "Model Reconstruction",
        "evidence_level": "Low",
        "category": "Risk Factor",
        "type": "MODEL_PARAMETER",
        "note": "Bonus points for local content compliance"
    },
    {
        "parameter": "Carbon Efficiency Threshold (High)",
        "variable": "CARBON_EFFICIENCY_THRESHOLD_HIGH",
        "value": 0.50,
        "unit": "kgCO2/USD",
        "source": "Model Reconstruction",
        "evidence_level": "Medium",
        "category": "Risk Factor",
        "type": "MODEL_PARAMETER",
        "note": "Threshold for maximum carbon bonus"
    },
    {
        "parameter": "Carbon Efficiency Threshold (Medium)",
        "variable": "CARBON_EFFICIENCY_THRESHOLD_MEDIUM",
        "value": 0.75,
        "unit": "kgCO2/USD",
        "source": "Model Reconstruction",
        "evidence_level": "Medium",
        "category": "Risk Factor",
        "type": "MODEL_PARAMETER",
        "note": "Threshold for partial carbon bonus"
    },
    {
        "parameter": "Carbon Efficiency Bonus (High)",
        "variable": "CARBON_BONUS_HIGH",
        "value": 10.0,
        "unit": "points",
        "source": "Model Reconstruction",
        "evidence_level": "Low",
        "category": "Risk Factor",
        "type": "MODEL_PARAMETER",
        "note": "Bonus for hitting high efficiency threshold"
    },
    {
        "parameter": "Carbon Efficiency Bonus (Medium)",
        "variable": "CARBON_BONUS_MEDIUM",
        "value": 5.0,
        "unit": "points",
        "source": "Model Reconstruction",
        "evidence_level": "Low",
        "category": "Risk Factor",
        "type": "MODEL_PARAMETER",
        "note": "Bonus for hitting medium efficiency threshold"
    },
    {
        "parameter": "Lead Time Threshold (High)",
        "variable": "LEAD_TIME_THRESHOLD_HIGH",
        "value": 14,
        "unit": "days",
        "source": "Model Reconstruction",
        "evidence_level": "Medium",
        "category": "Risk Factor",
        "type": "MODEL_PARAMETER",
        "note": "Threshold for max lead time bonus"
    },
    {
        "parameter": "Lead Time Threshold (Medium)",
        "variable": "LEAD_TIME_THRESHOLD_MEDIUM",
        "value": 21,
        "unit": "days",
        "source": "Model Reconstruction",
        "evidence_level": "Medium",
        "category": "Risk Factor",
        "type": "MODEL_PARAMETER",
        "note": "Threshold for partial lead time bonus"
    },
    {
        "parameter": "Lead Time Bonus (High)",
        "variable": "LEAD_TIME_BONUS_HIGH",
        "value": 10.0,
        "unit": "points",
        "source": "Model Reconstruction",
        "evidence_level": "Low",
        "category": "Risk Factor",
        "type": "MODEL_PARAMETER",
        "note": "Bonus for excellent lead time"
    },
    {
        "parameter": "Lead Time Bonus (Medium)",
        "variable": "LEAD_TIME_BONUS_MEDIUM",
        "value": 5.0,
        "unit": "points",
        "source": "Model Reconstruction",
        "evidence_level": "Low",
        "category": "Risk Factor",
        "type": "MODEL_PARAMETER",
        "note": "Bonus for acceptable lead time"
    },
    {
        "parameter": "High Risk ESG Threshold",
        "variable": "ESG_HIGH_RISK_THRESHOLD",
        "value": 75.0,
        "unit": "points",
        "source": "Petrosea Vendor Management Guidelines",
        "evidence_level": "Medium",
        "category": "Risk Factor",
        "type": "REPORTED",
        "note": "Suppliers below this score require audit"
    },
    # --- MODEL OPTIMIZATION BOUNDS ---
    {
        "parameter": "Max Biofuel Mix",
        "variable": "MAX_BIOFUEL_MIX",
        "value": 100.0,
        "unit": "%",
        "source": "Model Assumption",
        "evidence_level": "Low",
        "category": "Operational",
        "type": "MODEL_PARAMETER",
        "note": "Maximum allowable B100 biodiesel substitution"
    },
    {
        "parameter": "Max Local Procurement",
        "variable": "MAX_LOCAL_PROCUREMENT",
        "value": 50.0,
        "unit": "%",
        "source": "Model Assumption",
        "evidence_level": "Low",
        "category": "Operational",
        "type": "MODEL_PARAMETER",
        "note": "Maximum share of goods sourced locally"
    },
    {
        "parameter": "Max Barge Modal Shift",
        "variable": "MAX_BARGE_MODAL_SHIFT",
        "value": 50.0,
        "unit": "%",
        "source": "Model Assumption",
        "evidence_level": "Low",
        "category": "Operational",
        "type": "MODEL_PARAMETER",
        "note": "Maximum freight volume shifted from road to barge"
    },
    {
        "parameter": "Max EV Retrofit",
        "variable": "MAX_EV_RETROFIT",
        "value": 50.0,
        "unit": "%",
        "source": "Model Assumption",
        "evidence_level": "Low",
        "category": "Operational",
        "type": "MODEL_PARAMETER",
        "note": "Maximum fleet converted to electric"
    },
    {
        "parameter": "Biofuel Overlap Factor",
        "variable": "BIOFUEL_OVERLAP_FACTOR",
        "value": 0.10,
        "unit": "fraction (0-1)",
        "source": "Model Reconstruction",
        "evidence_level": "Low",
        "category": "Operational",
        "type": "MODEL_PARAMETER",
        "note": "Reduces biofuel effectiveness on vehicles already converted to EV"
    }
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
