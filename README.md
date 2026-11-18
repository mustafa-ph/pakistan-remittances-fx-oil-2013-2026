# Pakistan Workers' Remittances, Exchange Rate Stability, Eid Seasonality, and Gulf Oil Cycles (2013–2026)

**Author:** Ghulam Mustafa Phulpoto ([ORCID: 0009-0008-2230-313X](https://orcid.org/0009-0008-2230-313X))  
**Location:** Khairpur Mirs / Sukkur, Sindh, Pakistan  

## Research Question
> *Did Pakistan's 2023–2026 exchange rate stability permanently shift remittances into formal banking channels, or do spikes still depend on Eid and Gulf oil cycles?*

## Repository Structure
```text
├── data/
│   ├── raw/
│   │   ├── BFER_Daily_Arch.xlsx
│   │   ├── Homeremit_Arch.xlsx
│   │   ├── Seasonally Adjusted Workers Remittances.csv
│   │   └── POILBREUSDM.csv
│   └── processed/
│       ├── Pakistan_Remittances_Corridors_Monthly_1972_2026.csv   # 652 monthly records (Jul 1972 – Oct 2026)
│       ├── Pakistan_FX_Daily_2013_2026.csv                        # 3,275 daily records (Jul 2013 – Oct 2026)
│       └── Pakistan_Remittances_FX_Oil_Master_Monthly_2013_2026.csv # 160 monthly records (Jul 2013 – Oct 2026)
├── scripts/
│   ├── 01_build_master_datasets.py   # Cleans and merges the SBP & FRED raw files (0 missing months)
│   ├── 02_econometric_analysis.py    # Runs stationarity tests, structural breaks, and regressions
│   └── 03_generate_figures.py        # Generates the 5 final charts (300 DPI)
├── results/
│   ├── adf_stationarity_tests.csv
│   ├── corridor_breakdown_crisis_vs_stability.csv
│   ├── regime_summary.csv
│   ├── crisis_vs_stability_tests.csv
│   ├── eid_seasonality_regression.csv
│   ├── chow_scan_remit_sa.csv
│   ├── model_level_remit_sa.csv
│   ├── model_growth_remit_sa.csv
│   ├── model_growth_gcc.csv
│   ├── model_growth_west.csv
│   └── econometric_report.txt
├── figures/
│   ├── Fig1_Remittances_Trend_and_Break.png
│   ├── Fig2_USDPKR_Level_and_Volatility.png
│   ├── Fig3_Eid_Seasonality_by_Regime.png
│   ├── Fig4_Corridor_Shifts_and_Shares.png
│   └── Fig5_Regression_Coefficients_GCC_vs_West.png
├── CITATION.cff
├── LICENSE
└── requirements.txt
```

## Data Sources
1. **State Bank of Pakistan (SBP) — Country-wise Workers' Remittances (`Homeremit_Arch.xlsx`)**: Monthly inflows in Million USD (Jul 1972 – Oct 2026). This includes Roshan Digital Account (RDA) conversions starting in September 2020.
2. **State Bank of Pakistan (SBP) EasyData — Seasonally Adjusted Workers' Remittances**: X12-ARIMA seasonally adjusted monthly series (Jul 2005 – Oct 2026).
3. **State Bank of Pakistan (SBP) — Daily Average Banks' Floating Exchange Rates (`BFER_Daily_Arch.xlsx`)**: Daily PKR exchange rates across 23 currencies (Jul 2, 2013 – Oct 30, 2026).
4. **FRED (`POILBREUSDM`)**: Monthly Global Price of Brent Crude, USD/barrel (Jan 1992 – Sep 2026).
5. **Hijri Calendar Dates (2013–2026)**: Verified Eid-ul-Fitr and Eid-ul-Adha dates from [InfoPlease Islamic Holidays (2010–2030)](https://www.infoplease.com/calendars/holidays/islamic-holidays).

## My Key Findings
* **A real shift into formal banking:** After September 2023, daily USD/PKR volatility dropped 15×—from **0.576%/day** during the 2022–2023 crisis down to **0.038%/day** (*p* < 0.0001). At the same time, seasonally adjusted remittances jumped by **+$841.5M/month** (from $2,335.6M to $3,177.1M), with a clear structural break right at September 2023.
* **Gulf countries rebounded the most:** Inflows from GCC countries rose **+38.9%** (UAE +59.5%, Saudi Arabia +37.0%). My regressions show that sudden PKR drops hurt GCC inflows (`-1.017`, *p* = 0.008), while Western corridors (USA, UK, EU) barely react to exchange rate swings (*p* = 0.680).
* **Bigger Eid spikes in formal channels:** Once the exchange rate stabilized, formal Eid-month surges jumped to **+5.9% above trend** in 2023–2026, compared to just **+0.8%** during the FX crisis.
* **A modest link to oil prices:** Monthly changes in Brent crude prices have a small, positive connection to overall remittance growth (`+0.161`, *p* = 0.048).

## How to Run This Yourself
If you want to reproduce my datasets, analysis, and charts from scratch, just install the dependencies and run the three scripts in order:

```bash
pip install -r requirements.txt
python scripts/01_build_master_datasets.py
python scripts/02_econometric_analysis.py
python scripts/03_generate_figures.py
```
