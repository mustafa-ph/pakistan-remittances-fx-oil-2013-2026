import os
import numpy as np
import pandas as pd
from scipy import stats

REPO_DIR = "/working_dir/c_8cf7b7291b3ff2c2/artifacts/repo"
DATA_PATH = os.path.join(REPO_DIR, "data", "processed", "Pakistan_Remittances_FX_Oil_Master_Monthly_2013_2026.csv")
RESULTS_DIR = os.path.join(REPO_DIR, "results")
os.makedirs(RESULTS_DIR, exist_ok=True)


def ols_hac(y, X, col_names, maxlags=3):
    """OLS with Newey-West HAC standard errors and Durbin-Watson stat."""
    y = np.asarray(y, dtype=float)
    X = np.asarray(X, dtype=float)
    n, k = X.shape
    XtX_inv = np.linalg.inv(X.T @ X)
    beta = XtX_inv @ (X.T @ y)
    resid = y - X @ beta

    S = np.zeros((k, k))
    for i in range(n):
        xi = X[i : i + 1, :].T
        S += (resid[i] ** 2) * (xi @ xi.T)
    for lag in range(1, maxlags + 1):
        w = 1.0 - lag / (maxlags + 1.0)
        for i in range(lag, n):
            xi = X[i : i + 1, :].T
            xlag = X[i - lag : i - lag + 1, :].T
            cov = resid[i] * resid[i - lag] * (xi @ xlag.T + xlag @ xi.T)
            S += w * cov

    V_hac = (n / (n - k)) * (XtX_inv @ S @ XtX_inv)
    se = np.sqrt(np.diag(V_hac))
    t_stat = beta / se
    p_val = 2.0 * (1.0 - stats.t.cdf(np.abs(t_stat), df=n - k))

    tss = np.sum((y - y.mean()) ** 2)
    rss = np.sum(resid ** 2)
    r2 = 1.0 - rss / tss
    adj_r2 = 1.0 - (1.0 - r2) * (n - 1) / (n - k)
    dw = np.sum(np.diff(resid) ** 2) / rss

    res_df = pd.DataFrame({
        "Variable": col_names,
        "Coef": beta,
        "HAC_SE": se,
        "t_stat": t_stat,
        "p_value": p_val,
    })
    return res_df, {"n": n, "k": k, "r2": r2, "adj_r2": adj_r2, "rss": rss, "dw": dw, "resid": resid}


def adf_test(series, max_lags=4, trend="c"):
    """Augmented Dickey-Fuller test with BIC lag selection."""
    y = np.asarray(series.dropna(), dtype=float)
    best_bic = np.inf
    best_res = None

    for p in range(0, max_lags + 1):
        dy = np.diff(y)
        y_lag1 = y[:-1]
        start = p
        dep = dy[start:]
        n_obs = len(dep)
        cols = [y_lag1[start:], np.ones(n_obs)]
        if trend == "ct":
            cols.append(np.arange(1, n_obs + 1, dtype=float))
        for lag in range(1, p + 1):
            cols.append(dy[start - lag : len(dy) - lag])
        X = np.column_stack(cols)
        k = X.shape[1]
        beta = np.linalg.lstsq(X, dep, rcond=None)[0]
        resid = dep - X @ beta
        rss = np.sum(resid ** 2)
        sigma2 = rss / (n_obs - k)
        cov = sigma2 * np.linalg.inv(X.T @ X)
        t_stat = beta[0] / np.sqrt(cov[0, 0])
        bic = n_obs * np.log(rss / n_obs) + k * np.log(n_obs)
        if bic < best_bic:
            best_bic = bic
            best_res = (t_stat, p, n_obs)

    t_stat, opt_lag, n_obs = best_res
    # Approximate 1%, 5%, 10% MacKinnon critical values (n~150)
    if trend == "ct":
        cv1, cv5, cv10 = -4.02, -3.44, -3.14
    else:
        cv1, cv5, cv10 = -3.47, -2.88, -2.58
    sig = "1%" if t_stat < cv1 else ("5%" if t_stat < cv5 else ("10%" if t_stat < cv10 else "Non-stationary"))
    return {"ADF_t": t_stat, "Lags_BIC": opt_lag, "N": n_obs, "CV_5pct": cv5, "Result": sig}


def chow_test(y, X, break_idx):
    y1, X1 = y[:break_idx], X[:break_idx]
    y2, X2 = y[break_idx:], X[break_idx:]
    k = X.shape[1]
    n = len(y)
    if len(y1) <= k + 2 or len(y2) <= k + 2:
        return np.nan, np.nan
    b_p = np.linalg.lstsq(X, y, rcond=None)[0]
    rss_p = np.sum((y - X @ b_p) ** 2)
    b1 = np.linalg.lstsq(X1, y1, rcond=None)[0]
    rss1 = np.sum((y1 - X1 @ b1) ** 2)
    b2 = np.linalg.lstsq(X2, y2, rcond=None)[0]
    rss2 = np.sum((y2 - X2 @ b2) ** 2)
    rss_u = rss1 + rss2
    f_stat = ((rss_p - rss_u) / k) / (rss_u / (n - 2 * k))
    p_val = 1.0 - stats.f.cdf(f_stat, k, n - 2 * k)
    return f_stat, p_val


def main():
    df = pd.read_csv(DATA_PATH, parse_dates=["date"])

    # Prepare log and growth variables
    df["ln_Remit_SA"] = np.log(df["Remit_SA_MUSD"])
    df["ln_GCC"] = np.log(df["GCC_Total"])
    df["ln_West"] = np.log(df["West_Anglo_EU"])
    df["ln_USDPKR"] = np.log(df["USDPKR_mean"])
    df["ln_Brent"] = np.log(df["Brent_USD_bbl"])

    df["d_ln_Remit_SA"] = df["ln_Remit_SA"].diff() * 100.0
    df["d_ln_GCC"] = df["ln_GCC"].diff() * 100.0
    df["d_ln_West"] = df["ln_West"].diff() * 100.0
    df["d_ln_Brent_lag1"] = df["Brent_mom_pct_lag1"]
    df["d_ln_Brent_lag2"] = df["Brent_mom_pct_lag2"]
    df["Seasonal_Log_Pct"] = np.log(df["Total_Cash_Flow"] / df["Remit_SA_MUSD"]) * 100.0
    df["Eid_x_PostSep2023"] = df["Eid_Any_Month"] * df["Post_Sep2023"]

    # 1. ADF Stationarity Tests
    adf_rows = []
    for name, s, tr in [
        ("ln(Remit_SA)", df["ln_Remit_SA"], "ct"),
        ("ln(GCC_Total)", df["ln_GCC"], "ct"),
        ("ln(West_Anglo_EU)", df["ln_West"], "ct"),
        ("ln(USDPKR_mean)", df["ln_USDPKR"], "ct"),
        ("ln(Brent_USD)", df["ln_Brent"], "c"),
        ("USDPKR_Daily_Vol_Pct", df["USDPKR_vol_daily_pct"], "c"),
        ("Seasonal_Log_Pct", df["Seasonal_Log_Pct"], "c"),
        ("d_ln(Remit_SA)", df["d_ln_Remit_SA"], "c"),
        ("d_ln(GCC_Total)", df["d_ln_GCC"], "c"),
        ("d_ln(West_Anglo_EU)", df["d_ln_West"], "c"),
        ("d_ln(USDPKR)", df["USDPKR_mom_pct"], "c"),
        ("d_ln(Brent_USD)", df["Brent_mom_pct"], "c"),
    ]:
        r = adf_test(s, max_lags=4, trend=tr)
        r["Series"] = name
        r["Spec"] = "Const+Trend" if tr == "ct" else "Const"
        adf_rows.append(r)
    adf_df = pd.DataFrame(adf_rows)[["Series", "Spec", "N", "Lags_BIC", "ADF_t", "CV_5pct", "Result"]].round(3)
    adf_df.to_csv(os.path.join(RESULTS_DIR, "adf_stationarity_tests.csv"), index=False)

    # 2. Corridor-level breakdown: Crisis (2022-2023Aug) vs FX Stability (2023Sep-2026Oct)
    c_df = df[df["Regime"] == "3_FX_Crisis_2022_2023Aug"]
    s_df = df[df["Regime"] == "4_FX_Stability_2023Sep_2026Oct"]
    corr_rows = []
    for col in ["Total_Cash_Flow", "Remit_SA_MUSD", "Saudi_Arabia", "UAE", "Other_GCC", "GCC_Total", "USA", "UK", "EU_Countries", "West_Anglo_EU"]:
        t_res = stats.ttest_ind(s_df[col], c_df[col], equal_var=False)
        corr_rows.append({
            "Corridor_MUSD": col,
            "Crisis_Mean": c_df[col].mean(),
            "Stability_Mean": s_df[col].mean(),
            "Abs_Change": s_df[col].mean() - c_df[col].mean(),
            "Pct_Change": (s_df[col].mean() / c_df[col].mean() - 1.0) * 100.0,
            "Welch_t": t_res.statistic,
            "Welch_p": t_res.pvalue,
        })
    corr_df = pd.DataFrame(corr_rows).round(4)
    corr_df.to_csv(os.path.join(RESULTS_DIR, "corridor_breakdown_crisis_vs_stability.csv"), index=False)

    # 3. Structural Break (Chow at Sep 2023 & Sup-F)
    y_sa = df["ln_Remit_SA"].values
    X_sb = np.column_stack([np.ones(len(df)), df["t_idx"].values])
    sep2023_idx = df.index[df["date"] == pd.Timestamp("2023-09-01")][0]
    f_sep23, p_sep23 = chow_test(y_sa, X_sb, sep2023_idx)

    trim = int(0.15 * len(df))
    f_scan = []
    for idx in range(trim, len(df) - trim):
        f_val, p_val = chow_test(y_sa, X_sb, idx)
        f_scan.append({"date": df.loc[idx, "date"], "F_stat": f_val, "p_val": p_val})
    f_scan_df = pd.DataFrame(f_scan)
    f_scan_df.to_csv(os.path.join(RESULTS_DIR, "chow_scan_remit_sa.csv"), index=False)
    max_row = f_scan_df.loc[f_scan_df["F_stat"].idxmax()]

    # 4. Eid Seasonality Persistence Regression
    X_eid = np.column_stack([
        np.ones(len(df)),
        df["Eid_Fitr_Month"].values,
        df["Eid_Adha_Month"].values,
        df["Post_Sep2023"].values,
        df["Eid_x_PostSep2023"].values,
    ])
    eid_res, eid_meta = ols_hac(
        df["Seasonal_Log_Pct"].values,
        X_eid,
        ["Intercept", "Eid_Fitr_Month", "Eid_Adha_Month", "Post_Sep2023", "Eid_Any_x_PostSep2023"],
        maxlags=3,
    )
    eid_res.to_csv(os.path.join(RESULTS_DIR, "eid_seasonality_regression.csv"), index=False)

    # 5. Growth Models (Total SA, GCC, West)
    reg_df = df.dropna(subset=["d_ln_Remit_SA", "USDPKR_mom_pct", "USDPKR_vol_daily_pct", "Brent_mom_pct", "d_ln_Brent_lag1", "d_ln_Brent_lag2"]).copy()
    X_gr = np.column_stack([
        np.ones(len(reg_df)),
        reg_df["USDPKR_mom_pct"].values,
        reg_df["USDPKR_vol_daily_pct"].values,
        reg_df["Brent_mom_pct"].values,
        reg_df["d_ln_Brent_lag1"].values,
        reg_df["d_ln_Brent_lag2"].values,
        reg_df["Eid_Any_Month"].values,
        reg_df["Post_Sep2023"].values,
    ])
    gr_cols = ["Intercept", "d_ln_USDPKR", "USDPKR_Daily_Vol_Pct", "d_ln_Brent_t", "d_ln_Brent_t1", "d_ln_Brent_t2", "Eid_Any_Month", "Post_Sep2023"]

    gr_sa, gr_sa_meta = ols_hac(reg_df["d_ln_Remit_SA"].values, X_gr, gr_cols, maxlags=3)
    gr_gcc, gr_gcc_meta = ols_hac(reg_df["d_ln_GCC"].values, X_gr, gr_cols, maxlags=3)
    gr_west, gr_west_meta = ols_hac(reg_df["d_ln_West"].values, X_gr, gr_cols, maxlags=3)
    gr_sa.to_csv(os.path.join(RESULTS_DIR, "model_growth_remit_sa.csv"), index=False)
    gr_gcc.to_csv(os.path.join(RESULTS_DIR, "model_growth_gcc.csv"), index=False)
    gr_west.to_csv(os.path.join(RESULTS_DIR, "model_growth_west.csv"), index=False)

    print("=== ADF STATIONARITY TESTS ===")
    print(adf_df.to_string(index=False))
    print("\n=== CORRIDOR BREAKDOWN: CRISIS (2022-2023Aug) vs STABILITY (2023Sep-2026Oct) ===")
    print(corr_df.to_string(index=False))
    print(f"\n=== CHOW STRUCTURAL BREAK: Sep 2023 F={f_sep23:.3f} (p={p_sep23:.3e}); Sup-F={max_row['F_stat']:.3f} at {max_row['date'].strftime('%Y-%m-%d')} ===")
    print(f"\n=== EID SEASONALITY PERSISTENCE (R2={eid_meta['r2']:.3f}, DW={eid_meta['dw']:.2f}, N={eid_meta['n']}) ===")
    print(eid_res.round(4).to_string(index=False))
    print(f"\n=== GROWTH MODEL: TOTAL SA (R2={gr_sa_meta['r2']:.3f}, DW={gr_sa_meta['dw']:.2f}, N={gr_sa_meta['n']}) ===")
    print(gr_sa.round(4).to_string(index=False))
    print(f"\n=== GROWTH MODEL: GCC (R2={gr_gcc_meta['r2']:.3f}, DW={gr_gcc_meta['dw']:.2f}, N={gr_gcc_meta['n']}) ===")
    print(gr_gcc.round(4).to_string(index=False))
    print(f"\n=== GROWTH MODEL: WEST (R2={gr_west_meta['r2']:.3f}, DW={gr_west_meta['dw']:.2f}, N={gr_west_meta['n']}) ===")
    print(gr_west.round(4).to_string(index=False))


if __name__ == "__main__":
    main()
