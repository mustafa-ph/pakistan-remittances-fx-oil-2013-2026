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
│       ├── Pakistan_Remittances_Corridors_Monthly_1972_2026.csv   # 652 monthly obs (Jul 1972 – Oct 2026)
│       ├── Pakistan_FX_Daily_2013_2026.csv                        # 3,275 daily obs (Jul 2013 – Oct 2026)
│       └── Pakistan_Remittances_FX_Oil_Master_Monthly_2013_2026.csv # 160 monthly obs (Jul 2013 – Oct 2026)
├── scripts/
│   ├── 01_build_master_datasets.py   # Cleans & harmonizes SBP & FRED raw files (0 missing months)
│   ├── 02_econometric_analysis.py    # ADF tests, regime tests, Chow/Sup-F breaks, Newey-West HAC OLS
│   └── 03_generate_figures.py        # Publication-grade 300 DPI figures
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
1. **State Bank of Pakistan (SBP) — Country-wise Workers' Remittances (`Homeremit_Arch.xlsx`)**: Monthly inflows in Million USD (Jul 1972 – Oct 2026). Includes Roshan Digital Account (RDA) conversions from September 2020 and remitter-country-basis classification from July 2019.
2. **State Bank of Pakistan (SBP) EasyData — Seasonally Adjusted Workers' Remittances**: X12-ARIMA seasonally adjusted monthly series (Jul 2005 – Oct 2026).
3. **State Bank of Pakistan (SBP) — Daily Average Banks' Floating Exchange Rates (`BFER_Daily_Arch.xlsx`)**: Daily PKR exchange rates across 23 currencies (Jul 2, 2013 – Oct 30, 2026).
4. **FRED (`POILBREUSDM`)**: Monthly Global Price of Brent Crude, USD/barrel (Jan 1992 – Sep 2026).
5. **Hijri Calendar Dates (2013–2026)**: Verified Eid-ul-Fitr and Eid-ul-Adha dates from [InfoPlease Islamic Holidays (2010–2030)](https://www.infoplease.com/calendars/holidays/islamic-holidays).

## Key Empirical Findings
1. **Permanent Formalization Surge & Volatility Collapse**: Post-September 2023 FX stabilization reduced daily USD/PKR volatility 15× from **0.576%/day** (Jan 2022–Aug 2023 crisis) to **0.038%/day** (Sep 2023–Oct 2026, Welch *t* = -5.57, *p* < 0.0001). Seasonally adjusted remittances rose **+$841.5M/month** ($2,335.6M to $3,177.1M, *p* < 0.0001), with a Chow structural break at September 2023 (*F* = 14.87, *p* = 1.22e-6).
2. **GCC Corridors Rebounded Most**: GCC inflows rose **+38.9%** (UAE +59.5%, Saudi Arabia +37.0%). In Newey-West HAC growth regressions, sudden PKR depreciation depresses GCC inflows (`-1.017`, *p* = 0.008), while Western corridors (USA, UK, EU) show no significant FX sensitivity (*p* = 0.680).
3. **Eid Seasonality Amplified in Formal Channels**: Formal Eid-month surges (`Total / SA`) widened to **+5.9% above trend** in 2023–2026 vs. **+0.8%** during the FX crisis (`Eid × Post-Sep 2023 = +5.62%`, *p* = 0.0501).
4. **Oil-Cycle Link**: Contemporaneous Brent crude growth shows a modest positive link with seasonally adjusted total remittance growth (`+0.161`, *p* = 0.048).

## Reproducibility
```bash
pip install -r requirements.txt
python scripts/01_build_master_datasets.py
python scripts/02_econometric_analysis.py
python scripts/03_generate_figures.py
```
