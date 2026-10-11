"""Raw World Bank WDI extract -> long and panel (country-year) format.

No cleaning decisions are made here: we only drop the footer/blank rows that
DataBank appends, convert '..' to NaN, and reshape. Every judgement call
(imputation, dropping variables, transformations) belongs in the notebook
and in CLEANING.md.
"""
import re
from pathlib import Path

import pandas as pd

RAW = Path("data/raw/P_Data_Extract_From_World_Development_Indicators__1_.xlsx")
OUT = Path("data/processed")
OUT.mkdir(parents=True, exist_ok=True)

raw = pd.read_excel(RAW, sheet_name="Data")          # 'Sheet1' is not part of the World Bank export
print("rows read:", len(raw))

# Footer lines such as 'Data from database...' / 'Last Updated: ...' have no Series Code
footer = raw[raw["Series Code"].isna()]
print("footer/blank rows dropped:", len(footer))
print(footer["Country Name"].dropna().tolist())
raw = raw.dropna(subset=["Series Code"])

year_cols = [c for c in raw.columns if "[YR" in c]
long = raw.melt(
    id_vars=["Country Name", "Country Code", "Series Name", "Series Code"],
    value_vars=year_cols, var_name="year", value_name="value",
)
long["year"] = long["year"].str.extract(r"(\d{4})").astype(int)
long["value"] = pd.to_numeric(long["value"].replace("..", pd.NA), errors="coerce")
long.to_csv(OUT / "wdi_long.csv", index=False)

panel = long.pivot(index=["Country Name", "Country Code", "year"],
                   columns="Series Code", values="value").reset_index()
panel.to_csv(OUT / "wdi_panel.csv", index=False)

print("long:", long.shape, "| panel:", panel.shape)
print("countries:", sorted(panel["Country Name"].unique()))
print("years:", panel["year"].min(), "-", panel["year"].max())
print("\nmissing cells per indicator (of", len(panel), "country-years):")
print(panel.drop(columns=["Country Name", "Country Code", "year"]).isna().sum().sort_values(ascending=False))
