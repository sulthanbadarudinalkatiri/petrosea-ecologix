"""
Centralized Scientific & Operational Constants for Petrosea EcoLogix
References:
- IPCC 2019 Refinement to 2006 Guidelines for National Greenhouse Gas Inventories
- DEFRA / UK DESNZ 2024 Greenhouse Gas Reporting Conversion Factors
- PT Petrosea Tbk Net-Zero Corporate Target 2030 (30% Abatement)
"""

# -----------------------------------------------------------------------------
# EMISSION ABATEMENT CONVERSION FACTORS (IPCC / DEFRA GUIDELINES)
# -----------------------------------------------------------------------------
# Net GHG reduction factor for B100 biodiesel substitution vs fossil diesel (Scope 1)
BIOFUEL_B100_ABATEMENT_FACTOR: float = 0.18

# Heavy equipment fleet electrification / EV retrofit efficiency gain (Scope 1)
EV_RETROFIT_ABATEMENT_FACTOR: float = 0.25

# Scope 3 Category 1 & 4 reduction from local supply chain optimization (GO LOCAL)
LOCAL_PROC_LOGISTICS_ABATEMENT_FACTOR: float = 0.35

# Scope 3 Category 4 reduction from maritime barge intermodal shift vs road trucking
BARGE_INTERMODAL_SHIFT_ABATEMENT_FACTOR: float = 0.38

# -----------------------------------------------------------------------------
# DEFAULT TARGETS & CARBON TAX BENCHMARKS
# -----------------------------------------------------------------------------
NET_ZERO_TARGET_PERCENTAGE: float = 30.0  # Petrosea 2030 Corporate Abatement Target (%)
DEFAULT_CARBON_PRICE_USD: float = 25.0    # Carbon tax / credit baseline price ($ USD / tCO2e)

# -----------------------------------------------------------------------------
# LOGISTICS & SUPPLIER SCORECARD NORMALIZATION BENCHMARKS
# -----------------------------------------------------------------------------
MAX_BENCHMARK_LEAD_TIME_DAYS: int = 60      # Maximum mining supply chain lead time benchmark (days)
MAX_BENCHMARK_CARBON_INTENSITY: float = 1.0   # Baseline maximum vendor carbon intensity (kgCO2 / $ USD)
ESG_HIGH_RISK_THRESHOLD: float = 75.0       # ESG Score below 75 requires priority audit

# -----------------------------------------------------------------------------
# REAL ENVIRONMENTAL IMPACT CONVERSION EQUIVALENCIES (KALIMANTAN ECOSYSTEM)
# -----------------------------------------------------------------------------
TREES_PLANTED_PER_TON_CO2: float = 45.45            # Mature rainforest trees planted in Borneo per tCO2e
DIESEL_TRUCKS_RETIRED_PER_TON_CO2: float = 0.217    # Heavy mining diesel haul trucks retired per tCO2e
HOMES_POWERED_PER_TON_CO2: float = 0.125            # Balikpapan households powered by clean energy per tCO2e
