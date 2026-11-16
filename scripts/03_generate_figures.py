import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

REPO_DIR = "/working_dir/c_8cf7b7291b3ff2c2/artifacts/repo"
DATA_PATH = os.path.join(REPO_DIR, "data", "processed", "Pakistan_Remittances_FX_Oil_Master_Monthly_2013_2026.csv")
RESULTS_DIR = os.path.join(REPO_DIR, "results")
FIG_DIR = os.path.join(REPO_DIR, "figures")
os.makedirs(FIG_DIR, exist_ok=True)

# Clean, restrained academic journal styling (no pastel boxes)
plt.rcParams.update({
    "font.family": "DejaVu Serif",
    "font.size": 9.5,
    "axes.facecolor": "#ffffff",
    "figure.facecolor": "#ffffff",
    "axes.edgecolor": "#222222",
    "axes.linewidth": 0.8,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.color": "#d9d9d9",
    "grid.alpha": 0.6,
    "grid.linestyle": ":",
    "grid.linewidth": 0.7,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "savefig.facecolor": "#ffffff",
})

NAVY = "#1b365d"
CRIMSON = "#a61c1c"
CHARCOAL = "#333333"
GRAY = "#7f7f7f"
SLATE = "#9aa5b1"


def add_regime_lines(ax, y_text_frac=0.95):
    """Add crisp black/gray vertical dashed lines for Jan 2022 and Sep 2023."""
    ymin, ymax = ax.get_ylim()
    y_pos = ymin + y_text_frac * (ymax - ymin)
    ax.axvline(pd.Timestamp("2022-01-01"), color="#555555", ls="--", lw=1.0)
    ax.axvline(pd.Timestamp("2023-09-01"), color="#111111", ls="--", lw=1.2)
    ax.text(pd.Timestamp("2021-11-15"), y_pos, "Jan 2022\nFX Crisis", ha="right", va="top", fontsize=8, color="#444444")
    ax.text(pd.Timestamp("2023-10-15"), y_pos, "Sep 2023\nFX Stabilization", ha="left", va="top", fontsize=8, color="#111111", fontweight="bold")


def make_fig1(df):
    fig, ax = plt.subplots(figsize=(9.5, 4.8))
    ax.plot(df["date"], df["Total_Cash_Flow"], color=GRAY, lw=1.0, alpha=0.85, label="Unadjusted Remittances (USD Million)")
    ax.plot(df["date"], df["Remit_SA_MUSD"], color=NAVY, lw=2.0, label="Seasonally Adjusted (X12-ARIMA, USD Million)")
    eid_pts = df[df["Eid_Any_Month"] == 1]
    ax.scatter(eid_pts["date"], eid_pts["Total_Cash_Flow"], color=CRIMSON, s=22, zorder=5, label="Eid-ul-Fitr / Eid-ul-Adha Month")

    ax.set_ylim(1000, 4650)
    add_regime_lines(ax, y_text_frac=0.96)
    ax.set_ylabel("Million USD per Month", fontsize=10, fontweight="bold")
    ax.set_title("Pakistan Workers' Remittances: Unadjusted vs. Seasonally Adjusted (Jul 2013 – Oct 2026)", fontsize=11, fontweight="bold", pad=10)
    ax.legend(loc="upper left", fontsize=8.5, frameon=True, edgecolor="#cccccc")
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    fig.savefig(os.path.join(FIG_DIR, "Fig1_Remittances_Trend_and_Break.png"))
    plt.close(fig)


def make_fig2(df):
    fig, ax1 = plt.subplots(figsize=(9.5, 4.6))
    ax2 = ax1.twinx()
    ax2.spines["top"].set_visible(False)
    ax2.grid(False)

    l1 = ax1.plot(df["date"], df["USDPKR_vol_daily_pct"], color=CRIMSON, lw=1.5, label="USD/PKR Daily Return Volatility (Std %, Left)")
    l2 = ax2.plot(df["date"], df["USDPKR_mean"], color=NAVY, lw=1.7, ls="-.", label="USD/PKR Monthly Mean Exchange Rate (Right)")

    ax1.set_ylim(-0.05, 2.35)
    add_regime_lines(ax1, y_text_frac=0.96)
    ax1.set_ylabel("Realized Daily Volatility (%)", fontsize=10, fontweight="bold", color=CRIMSON)
    ax2.set_ylabel("PKR per USD", fontsize=10, fontweight="bold", color=NAVY)
    ax1.set_title("USD/PKR Exchange Rate Level and Realized Daily Volatility (Jul 2013 – Oct 2026)", fontsize=11, fontweight="bold", pad=10)

    lines = l1 + l2
    ax1.legend(lines, [l.get_label() for l in lines], loc="upper left", fontsize=8.5, frameon=True, edgecolor="#cccccc")
    ax1.xaxis.set_major_locator(mdates.YearLocator(2))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    fig.savefig(os.path.join(FIG_DIR, "Fig2_USDPKR_Level_and_Volatility.png"))
    plt.close(fig)


def make_fig3(df):
    regime_order = [
        ("1_Managed_Peg_2013_2017", "Managed Peg\n(2013–2017)"),
        ("2_Float_COVID_2018_2021", "Float & COVID\n(2018–2021)"),
        ("3_FX_Crisis_2022_2023Aug", "FX Crisis\n(2022–Aug 2023)"),
        ("4_FX_Stability_2023Sep_2026Oct", "FX Stability\n(Sep 2023–Oct 2026)"),
    ]
    x = np.arange(len(regime_order))
    w = 0.34
    eid_means, noneid_means, eid_se, noneid_se = [], [], [], []
    for r_key, _ in regime_order:
        sub = df[df["Regime"] == r_key]
        e = (sub[sub["Eid_Any_Month"] == 1]["Seasonal_Factor_Ratio"] - 1.0) * 100.0
        ne = (sub[sub["Eid_Any_Month"] == 0]["Seasonal_Factor_Ratio"] - 1.0) * 100.0
        eid_means.append(e.mean())
        noneid_means.append(ne.mean())
        eid_se.append(e.std(ddof=1) / np.sqrt(len(e)))
        noneid_se.append(ne.std(ddof=1) / np.sqrt(len(ne)))

    fig, ax = plt.subplots(figsize=(8.5, 4.5))
    ax.bar(x - w / 2, eid_means, w, yerr=eid_se, capsize=4, color=NAVY, edgecolor="#111111", lw=0.6, label="Eid Month (Eid-ul-Fitr / Eid-ul-Adha)")
    ax.bar(x + w / 2, noneid_means, w, yerr=noneid_se, capsize=4, color=SLATE, edgecolor="#444444", lw=0.6, label="Non-Eid Month")
    ax.axhline(0, color="#222222", lw=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels([lbl for _, lbl in regime_order], fontsize=9)
    ax.set_ylabel("Seasonal Surge Above SA Trend (%)", fontsize=10, fontweight="bold")
    ax.set_title("Eid Remittance Surge Across Exchange Rate Regimes (Mean ± SE)", fontsize=11, fontweight="bold", pad=10)
    ax.legend(loc="upper left", fontsize=8.5, frameon=True, edgecolor="#cccccc")
    fig.savefig(os.path.join(FIG_DIR, "Fig3_Eid_Seasonality_by_Regime.png"))
    plt.close(fig)


def make_fig4(df):
    fig, ax = plt.subplots(figsize=(9.5, 4.6))
    ax.plot(df["date"], df["GCC_Share_Pct"], color=NAVY, lw=1.9, label="GCC Corridors (% of Total Cash Flow)")
    ax.plot(df["date"], df["West_Share_Pct"], color=CRIMSON, lw=1.9, ls="--", label="Western Corridors: USA, UK, EU, CAN, AUS (%)")

    ax.set_ylim(20, 72)
    add_regime_lines(ax, y_text_frac=0.96)
    ax.set_ylabel("Share of Total Remittances (%)", fontsize=10, fontweight="bold")
    ax.set_title("Corridor Composition: GCC Rebound vs. Western Corridors (Jul 2013 – Oct 2026)", fontsize=11, fontweight="bold", pad=10)
    ax.legend(loc="lower left", fontsize=8.5, frameon=True, edgecolor="#cccccc")
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    fig.savefig(os.path.join(FIG_DIR, "Fig4_Corridor_Shifts_and_Shares.png"))
    plt.close(fig)


def make_fig5():
    gcc = pd.read_csv(os.path.join(RESULTS_DIR, "model_growth_gcc.csv"))
    west = pd.read_csv(os.path.join(RESULTS_DIR, "model_growth_west.csv"))

    vars_keep = ["d_ln_USDPKR", "d_ln_Brent_t", "d_ln_Brent_t1", "Eid_Any_Month", "Post_Sep2023"]
    labels = [
        "USD/PKR Monthly\nDepreciation (%)",
        "Brent Crude Oil\nGrowth (t, %)",
        "Brent Crude Oil\nGrowth (t-1, %)",
        "Eid Month\nIndicator",
        "Post-Sep 2023\nStability Regime",
    ]

    g_sub = gcc.set_index("Variable").loc[vars_keep]
    w_sub = west.set_index("Variable").loc[vars_keep]

    y = np.arange(len(vars_keep))
    offset = 0.16

    fig, ax = plt.subplots(figsize=(8.8, 4.6))
    ax.errorbar(g_sub["Coef"], y - offset, xerr=1.96 * g_sub["HAC_SE"], fmt="o", color=NAVY, capsize=4, lw=1.5, ms=6, label="GCC Corridors (R² = 0.130)")
    ax.errorbar(w_sub["Coef"], y + offset, xerr=1.96 * w_sub["HAC_SE"], fmt="s", color=CRIMSON, capsize=4, lw=1.5, ms=5.5, label="Western Corridors (R² = 0.047)")
    ax.axvline(0, color="#222222", lw=0.9, ls="-")
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=9)
    ax.invert_yaxis()
    ax.set_xlabel("Monthly Growth Effect (% pts, 95% Newey-West HAC CI)", fontsize=10, fontweight="bold")
    ax.set_title("Corridor Heterogeneity in Monthly Remittance Growth (Newey-West HAC)", fontsize=11, fontweight="bold", pad=10)
    ax.legend(loc="lower left", fontsize=8.5, frameon=True, edgecolor="#cccccc")
    fig.savefig(os.path.join(FIG_DIR, "Fig5_Regression_Coefficients_GCC_vs_West.png"))
    plt.close(fig)


if __name__ == "__main__":
    df = pd.read_csv(DATA_PATH, parse_dates=["date"])
    make_fig1(df)
    make_fig2(df)
    make_fig3(df)
    make_fig4(df)
    make_fig5()
    print("Generated 5 separate academic-style figures in", FIG_DIR)
