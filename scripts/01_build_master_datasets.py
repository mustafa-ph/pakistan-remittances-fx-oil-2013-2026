import os
import re
import datetime
import numpy as np
import pandas as pd

BASE_UPLOAD = "/working_dir/c_8cf7b7291b3ff2c2/user_uploaded_files/ttl=63d/user_uploaded"
REPO_DIR = "/working_dir/c_8cf7b7291b3ff2c2/artifacts/repo"
DATA_CLEAN_DIR = os.path.join(REPO_DIR, "data", "processed")
os.makedirs(DATA_CLEAN_DIR, exist_ok=True)


def parse_homeremit_date(val):
    if isinstance(val, (datetime.datetime, pd.Timestamp)):
        return pd.Timestamp(val.year, val.month, 1)
    if isinstance(val, str):
        s = val.strip()
        if s.upper().startswith("FY"):
            return None
        s_clean = re.sub(r"[Rr\*]+$", "", s).strip()
        for fmt in ("%b-%y", "%B-%y", "%b-%Y", "%B-%Y", "%Y-%m-%d", "%d-%b-%Y"):
            try:
                dt = datetime.datetime.strptime(s_clean, fmt)
                return pd.Timestamp(dt.year, dt.month, 1)
            except ValueError:
                pass
    return None


def clean_homeremit():
    path = os.path.join(BASE_UPLOAD, "Homeremit_Arch.xlsx")
    sheets = ["Jul 72 to  Jun 10", "July 2010- Jun 2018", "July 2018 onwards "]

    label_map = {
        "Cash Flow": "Total_Cash_Flow",
        "Cash": "Total_Cash_Flow",
        "Total": "Total_Remittances",
        "Total (I+II)": "Total_Remittances",
        "USA": "USA",
        "U.K.": "UK",
        "Saudi Arabia": "Saudi_Arabia",
        "U.A.E.": "UAE",
        "Dubai": "UAE_Dubai",
        "Abu Dhabi": "UAE_Abu_Dhabi",
        "Sharjah": "UAE_Sharjah",
        "Others": "UAE_Others",
        "Other GCC Countries": "Other_GCC",
        "Behrain": "Bahrain",
        "Bahrain": "Bahrain",
        "Kuwait": "Kuwait",
        "Qatar": "Qatar",
        "Oman": "Oman",
        "EU Countryies": "EU_Countries",
        "EU Countries": "EU_Countries",
        "Germany": "Germany",
        "France": "France",
        "Netherland": "Netherlands",
        "Spain": "Spain",
        "Italy": "Italy",
        "Greece": "Greece",
        "Sweden": "Sweden",
        "Denmark": "Denmark",
        "Ireland": "Ireland",
        "Belgium": "Belgium",
        "Malaysia*": "Malaysia",
        "Norway": "Norway",
        "Switzerland": "Switzerland",
        "Australia": "Australia",
        "Canada": "Canada",
        "Japan": "Japan",
        "South Africa*": "South_Africa",
        "South Korea*": "South_Korea",
        "Others Countries": "Other_Countries",
        "Other Countries#": "Other_Countries",
    }

    records = {}
    for sh in sheets:
        df = pd.read_excel(path, sheet_name=sh, header=None)
        header_row = df.iloc[4]
        date_cols = {}
        for c_idx in range(3, df.shape[1]):
            dt = parse_homeremit_date(header_row.iloc[c_idx])
            if dt is not None:
                date_cols[c_idx] = dt

        for r_idx in range(5, df.shape[0]):
            c0 = str(df.iloc[r_idx, 0]).strip() if pd.notna(df.iloc[r_idx, 0]) else ""
            c1 = str(df.iloc[r_idx, 1]).strip() if pd.notna(df.iloc[r_idx, 1]) else ""
            c2 = str(df.iloc[r_idx, 2]).strip() if pd.notna(df.iloc[r_idx, 2]) else ""

            raw_label = None
            if c2 in label_map:
                raw_label = c2
            elif c1 in label_map:
                raw_label = c1
            elif c0 in label_map:
                raw_label = c0
            if raw_label is None:
                continue
            canon = label_map[raw_label]

            for c_idx, dt in date_cols.items():
                val = pd.to_numeric(df.iloc[r_idx, c_idx], errors="coerce")
                if dt not in records:
                    records[dt] = {"date": dt}
                records[dt][canon] = val

    out = pd.DataFrame(sorted(records.values(), key=lambda x: x["date"]))
    out = out.sort_values("date").reset_index(drop=True)
    out["GCC_Total"] = out[["Saudi_Arabia", "UAE", "Other_GCC"]].sum(axis=1, min_count=1)
    out["West_Anglo_EU"] = out[["USA", "UK", "EU_Countries", "Canada", "Australia"]].sum(axis=1, min_count=1)
    out["GCC_Share_Pct"] = (out["GCC_Total"] / out["Total_Cash_Flow"]) * 100.0
    out["West_Share_Pct"] = (out["West_Anglo_EU"] / out["Total_Cash_Flow"]) * 100.0

    # Verify zero missing months
    full_range = pd.date_range(out["date"].min(), out["date"].max(), freq="MS")
    missing_months = full_range.difference(out["date"])
    assert len(missing_months) == 0, f"Missing months found: {missing_months}"

    out_path = os.path.join(DATA_CLEAN_DIR, "Pakistan_Remittances_Corridors_Monthly_1972_2026.csv")
    out.to_csv(out_path, index=False)
    print(f"Saved Remittances Corridors: {out.shape}, {out['date'].min().date()} to {out['date'].max().date()} (0 missing months)")
    return out


def clean_sa_remittances():
    path = os.path.join(BASE_UPLOAD, "Seasonally Adjusted Workers Remittances.csv")
    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["Observation Date"], format="%d-%b-%Y").dt.to_period("M").dt.to_timestamp()
    df["Remit_SA_MUSD"] = pd.to_numeric(df["Observation Value"], errors="coerce")
    df = df[["date", "Remit_SA_MUSD"]].sort_values("date").reset_index(drop=True)
    print(f"Loaded SA Remittances: {df.shape}, {df['date'].min().date()} to {df['date'].max().date()}")
    return df


def clean_bfer_daily():
    path = os.path.join(BASE_UPLOAD, "BFER_Daily_Arch.xlsx")
    df = pd.read_excel(path, sheet_name="Sheet2", header=None)
    dates = pd.to_datetime(df.iloc[6, 2:].values)
    rows = df.iloc[7:30]

    data = {"date": dates}
    for _, r in rows.iterrows():
        country = str(r.iloc[0]).strip()
        col_name = re.sub(r"[^A-Za-z0-9]+", "_", country).strip("_")
        vals = pd.to_numeric(r.iloc[2:].values, errors="coerce")
        data[f"PKR_per_{col_name}"] = vals

    daily = pd.DataFrame(data).sort_values("date").reset_index(drop=True)
    daily_path = os.path.join(DATA_CLEAN_DIR, "Pakistan_FX_Daily_2013_2026.csv")
    daily.to_csv(daily_path, index=False)
    print(f"Saved Daily FX: {daily.shape}, {daily['date'].min().date()} to {daily['date'].max().date()}")

    daily["ym"] = daily["date"].dt.to_period("M").dt.to_timestamp()
    key_cols = ["PKR_per_U_S_A", "PKR_per_Saudi_Arabia", "PKR_per_U_A_E", "PKR_per_U_K", "PKR_per_EMU"]
    short_names = {
        "PKR_per_U_S_A": "USDPKR",
        "PKR_per_Saudi_Arabia": "SARPKR",
        "PKR_per_U_A_E": "AEDPKR",
        "PKR_per_U_K": "GBPPKR",
        "PKR_per_EMU": "EURPKR",
    }

    for c in key_cols:
        daily[f"{c}_ret"] = np.log(daily[c] / daily[c].shift(1)) * 100.0

    monthly_parts = []
    for c in key_cols:
        sn = short_names[c]
        grp = daily.groupby("ym")
        part = pd.DataFrame({
            f"{sn}_mean": grp[c].mean(),
            f"{sn}_eom": grp[c].last(),
            f"{sn}_vol_daily_pct": grp[f"{c}_ret"].std(),
            f"{sn}_range_pct": (grp[c].max() - grp[c].min()) / grp[c].mean() * 100.0,
            f"{sn}_n_days": grp[c].count(),
        })
        part[f"{sn}_mom_pct"] = np.log(part[f"{sn}_eom"] / part[f"{sn}_eom"].shift(1)) * 100.0
        part[f"{sn}_yoy_pct"] = (part[f"{sn}_mean"] / part[f"{sn}_mean"].shift(12) - 1.0) * 100.0
        monthly_parts.append(part)

    fx_m = pd.concat(monthly_parts, axis=1).reset_index().rename(columns={"ym": "date"})
    return fx_m


def clean_brent_oil():
    path = os.path.join(BASE_UPLOAD, "POILBREUSDM.csv")
    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["observation_date"]).dt.to_period("M").dt.to_timestamp()
    df["Brent_USD_bbl"] = pd.to_numeric(df["POILBREUSDM"], errors="coerce")
    df = df[["date", "Brent_USD_bbl"]].sort_values("date").reset_index(drop=True)
    df["Brent_mom_pct"] = np.log(df["Brent_USD_bbl"] / df["Brent_USD_bbl"].shift(1)) * 100.0
    df["Brent_yoy_pct"] = (df["Brent_USD_bbl"] / df["Brent_USD_bbl"].shift(12) - 1.0) * 100.0
    for lag in [1, 2, 3]:
        df[f"Brent_USD_bbl_lag{lag}"] = df["Brent_USD_bbl"].shift(lag)
        df[f"Brent_mom_pct_lag{lag}"] = df["Brent_mom_pct"].shift(lag)
    print(f"Loaded Brent Oil: {df.shape}, {df['date'].min().date()} to {df['date'].max().date()}")
    return df


if __name__ == "__main__":
    remit = clean_homeremit()
    sa = clean_sa_remittances()
    fx_m = clean_bfer_daily()
    oil = clean_brent_oil()

    master = remit.merge(sa, on="date", how="left").merge(fx_m, on="date", how="left").merge(oil, on="date", how="left")
    master["Seasonal_Factor_Ratio"] = master["Total_Cash_Flow"] / master["Remit_SA_MUSD"]
    master["Seasonal_Excess_MUSD"] = master["Total_Cash_Flow"] - master["Remit_SA_MUSD"]

    master_2013 = master[master["date"] >= "2013-07-01"].copy().reset_index(drop=True)
    master_path = os.path.join(DATA_CLEAN_DIR, "Pakistan_Remittances_FX_Oil_Master_Monthly_2013_2026.csv")
    master_2013.to_csv(master_path, index=False)
    print(f"Saved Master Monthly (2013-2026): {master_2013.shape}, {master_2013['date'].min().date()} to {master_2013['date'].max().date()}")
    print("Missing check in Master 2013-2026 (key cols):")
    print(master_2013[["Total_Cash_Flow", "Remit_SA_MUSD", "USDPKR_mean", "USDPKR_vol_daily_pct", "Brent_USD_bbl"]].isnull().sum())
