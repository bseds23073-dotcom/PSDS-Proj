"""Cleaning checks, EDA and a baseline prediction model for the under-5 mortality panel.

Run from the repository root AFTER src/load_and_reshape.py:
    python src/clean_and_eda.py
Reads data/processed/wdi_panel.csv, writes data/processed/analysis_sample.csv and figures/*.png.
"""
from pathlib import Path
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import skew
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.metrics import mean_absolute_error, r2_score

FIG = Path("figures"); FIG.mkdir(exist_ok=True)
NAMES = {"SH.DYN.MORT": "u5mr", "SE.SEC.ENRR.FE": "fem_sec_enrol", "NY.GDP.PCAP.PP.KD": "gdp_pc_ppp",
         "SH.XPD.CHEX.GD.ZS": "health_exp_gdp", "SP.DYN.TFRT.IN": "fertility", "SH.STA.BASS.ZS": "sanitation",
         "SH.H2O.BASW.ZS": "water", "EG.ELC.ACCS.ZS": "electricity", "SH.IMM.MEAS": "measles_imm",
         "SP.URB.TOTL.IN.ZS": "urban_pct", "SE.ADT.LITR.FE.ZS": "fem_literacy", "SH.STA.BRTC.ZS": "skilled_birth",
         "SL.UEM.TOTL.ZS": "unemployment", "SH.XPD.GHED.GD.ZS": "gov_health_exp_gdp"}
df = pd.read_csv("data/processed/wdi_panel.csv").rename(columns=NAMES).rename(columns={"Country Name": "country", "Country Code": "code"})
ind = list(NAMES.values())

print("=== SIX THINGS ===")
print("1 missing cells per indicator:\n", df[ind].isna().sum().sort_values(ascending=False).head(4).to_string())
print("2 duplicated country-year rows:", df.duplicated(["code", "year"]).sum())
print("3 dtypes not numeric:", [c for c in ind if not pd.api.types.is_numeric_dtype(df[c])])
pct = ["fem_sec_enrol", "sanitation", "water", "electricity", "measles_imm", "urban_pct", "fem_literacy", "skilled_birth"]
print("4 percent columns outside 0-100:", int(((df[pct] < 0) | (df[pct] > 100)).sum().sum()),
      "| u5mr range", df.u5mr.min(), df.u5mr.max())
print("5 country names with stray whitespace/non-ascii:", [c for c in df.country.unique() if c != c.strip() or not c.isascii()])
jump = df.sort_values(["code", "year"]).groupby("code")[ind].diff().abs().max()
rel = (df.sort_values(["code", "year"]).groupby("code")[ind].pct_change(fill_method=None).abs().max())
print("6 largest single-year relative jump, top 3:\n", rel.sort_values(ascending=False).head(3).round(2).to_string())
for s in ["u5mr", "gdp_pc_ppp"]:
    print("   max abs yoy change", s, round(jump[s], 2))
print("regional aggregates present:", [c for c in df.country.unique() if c not in ["Pakistan", "India", "Bangladesh", "Nepal", "Sri Lanka"]])

print("\n=== MISSINGNESS PATTERN (enrolment) ===")
miss = df[df.fem_sec_enrol.isna()].groupby("country").year.apply(list)
print(miss.to_string())
print("rows with enrolment:", df.fem_sec_enrol.notna().sum(), "of", len(df))
for v in ["fem_literacy", "skilled_birth"]:
    print(v, "non-missing years by country:", df.groupby("country")[v].apply(lambda s: int(s.notna().sum())).to_dict())
early = df[df.year <= 2011].fem_sec_enrol.isna().mean(); late = df[df.year > 2011].fem_sec_enrol.isna().mean()
print("enrolment missing share 2000-2011: %.2f, 2012-2023: %.2f" % (early, late))
m = df.assign(miss=df.fem_sec_enrol.isna()).groupby("miss")[["u5mr", "gdp_pc_ppp"]].mean().round(1)
print("mean u5mr / GDP for rows with vs without enrolment:\n", m.to_string())

print("\n=== TRANSFORMATION ===")
df["log_gdp"] = np.log(df.gdp_pc_ppp)
print("skew gdp_pc_ppp %.2f -> log %.2f" % (skew(df.gdp_pc_ppp), skew(df.log_gdp)))

print("\n=== CONFOUNDER CHECK: female secondary enrolment vs u5mr ===")
s = df.dropna(subset=["fem_sec_enrol"]).copy()
print("complete-case rows:", len(s))
print("pooled corr: %.2f" % s.fem_sec_enrol.corr(s.u5mr))
print("by country corr:", s.groupby("country").apply(lambda g: round(g.fem_sec_enrol.corr(g.u5mr), 2), include_groups=False).to_dict())
def ols(cols, data=s):
    X = pd.get_dummies(data[cols + (["country"] if "FE" in FE else [])], drop_first=True, dtype=float) if False else None
def fit(data, xs, fe=False, yr=False):
    X = data[xs].copy()
    if yr: X["year"] = data.year
    if fe: X = pd.concat([X, pd.get_dummies(data.country, drop_first=True, dtype=float)], axis=1)
    X.insert(0, "const", 1.0)
    b, *_ = np.linalg.lstsq(X.values, data.u5mr.values, rcond=None)
    return dict(zip(X.columns, b))[xs[0]]
print("coef on enrolment (u5mr points per +1 pp):")
print("  (a) alone            %.2f" % fit(s, ["fem_sec_enrol"]))
print("  (b) + country FE     %.2f" % fit(s, ["fem_sec_enrol"], fe=True))
print("  (c) + FE + log GDP   %.2f" % fit(s, ["fem_sec_enrol", "log_gdp"], fe=True))
print("  (d) + FE + logGDP + year trend %.2f" % fit(s, ["fem_sec_enrol", "log_gdp"], fe=True, yr=True))
print("  (e) + FE + year only %.2f" % fit(s, ["fem_sec_enrol"], fe=True, yr=True))
print("  (f) drop Sri Lanka, FE+logGDP %.2f" % fit(s[s.country != "Sri Lanka"], ["fem_sec_enrol", "log_gdp"], fe=True))

print("\n=== PREDICTION ===")
base = ["log_gdp", "health_exp_gdp", "gov_health_exp_gdp", "fertility", "sanitation", "water", "electricity", "measles_imm", "urban_pct", "unemployment"]
def models():
    return {"mean baseline": None, "ridge": make_pipeline(StandardScaler(), Ridge(alpha=1.0)),
            "random forest": RandomForestRegressor(n_estimators=300, random_state=0, min_samples_leaf=2)}
def evaluate(data, feats, splits):
    out = []
    for name, mdl in models().items():
        yt, yp = [], []
        for tr, te in splits(data):
            if mdl is None: p = np.full(len(te), data.loc[tr, "u5mr"].mean())
            else: mdl.fit(data.loc[tr, feats], data.loc[tr, "u5mr"]); p = mdl.predict(data.loc[te, feats])
            yt += list(data.loc[te, "u5mr"]); yp += list(p)
        out.append((name, mean_absolute_error(yt, yp), r2_score(yt, yp)))
    return out
time_split = lambda d: [(d.index[d.year <= 2015], d.index[d.year > 2015])]
loco = lambda d: [(d.index[d.country != c], d.index[d.country == c]) for c in d.country.unique()]
d_all = df.copy()
for label, d, f in [("all 120 rows, base features", d_all, base), ("98 complete rows, base", s, base), ("98 complete rows, base + enrolment", s, base + ["fem_sec_enrol"])]:
    for sp_name, sp in [("time split (train<=2015, test 2016-23)", time_split), ("leave-one-country-out", loco)]:
        print(label, "|", sp_name)
        for n, mae, r2 in evaluate(d.reset_index(drop=True) if False else d, f, sp): print("   %-14s MAE %.1f  R2 %.2f" % (n, mae, r2))
print("LOCO per held-out country (ridge, base features, 120 rows):")
for c in df.country.unique():
    tr, te = df.index[df.country != c], df.index[df.country == c]
    m_ = make_pipeline(StandardScaler(), Ridge(alpha=1.0)).fit(df.loc[tr, base], df.loc[tr, "u5mr"])
    print("   %-11s MAE %.1f" % (c, mean_absolute_error(df.loc[te, "u5mr"], m_.predict(df.loc[te, base]))))

print("\nSENSITIVITY: drop unemployment (Pakistan series jumps 0.80 -> 3.67 in 2012), all 120 rows")
b2 = [f for f in base if f != "unemployment"]
for sp_name, sp in [("time split", time_split), ("leave-one-country-out", loco)]:
    print(" ", sp_name)
    for n, mae, r2 in evaluate(df, b2, sp): print("   %-14s MAE %.1f  R2 %.2f" % (n, mae, r2))

s.to_csv("data/processed/analysis_sample.csv", index=False)

# ---------------- charts ----------------
col = {"Pakistan": "#01411C", "India": "#E07B00", "Bangladesh": "#B00020", "Nepal": "#5B3F8C", "Sri Lanka": "#1F77B4"}
fig, ax = plt.subplots(figsize=(7, 4))
for c, g in df.groupby("country"): ax.plot(g.year, g.u5mr, label=c, color=col[c], lw=2)
ax.set_title("Under-5 mortality fell in all five countries, but Pakistan stays highest", loc="left", fontsize=11, fontweight="bold")
ax.set_ylabel("Deaths per 1,000 live births"); ax.legend(frameon=False); ax.spines[["top", "right"]].set_visible(False)
fig.text(0.01, 0.01, "Modelled UN IGME estimates via WDI, 2000-2023.", fontsize=8); fig.tight_layout(rect=(0, 0.04, 1, 1)); fig.savefig(FIG / "01_u5mr_trends.png", dpi=150)

fig, ax = plt.subplots(figsize=(8, 3.6)); names = {"fem_sec_enrol": "Female sec. enrolment", "fem_literacy": "Female literacy", "skilled_birth": "Skilled birth attendance"}
rows, labels = [], []
for c in df.country.unique():
    for v in names: rows.append(df[df.country == c].sort_values("year")[v].notna().astype(int).values); labels.append(f"{c} - {names[v]}")
ax.imshow(np.array(rows), aspect="auto", cmap="Greys", vmin=0, vmax=1.6); ax.set_yticks(range(len(labels))); ax.set_yticklabels(labels, fontsize=6)
ax.set_xticks(range(0, 24, 3)); ax.set_xticklabels(range(2000, 2024, 3))
ax.set_title("Education and birth-care data have large gaps, worst for Sri Lanka's enrolment", loc="left", fontsize=10, fontweight="bold")
fig.text(0.01, 0.01, "Dark = value present, white = missing.", fontsize=8); fig.tight_layout(rect=(0, 0.04, 1, 1)); fig.savefig(FIG / "02_missingness_map.png", dpi=150)

fig, axs = plt.subplots(1, 2, figsize=(9, 4), sharey=True)
for c, g in s.groupby("country"): axs[0].scatter(g.fem_sec_enrol, g.u5mr, color=col[c], s=14, label=c); axs[1].scatter(g.fem_sec_enrol, g.u5mr, color=col[c], s=14)
for c, g in s.groupby("country"):
    k = np.polyfit(g.fem_sec_enrol, g.u5mr, 1); xs = np.linspace(g.fem_sec_enrol.min(), g.fem_sec_enrol.max(), 10); axs[1].plot(xs, np.polyval(k, xs), color=col[c])
k = np.polyfit(s.fem_sec_enrol, s.u5mr, 1); xs = np.linspace(s.fem_sec_enrol.min(), s.fem_sec_enrol.max(), 10); axs[0].plot(xs, np.polyval(k, xs), color="k", ls="--")
axs[0].set_title("Pooled: steep negative slope", fontsize=10); axs[1].set_title("Within each country: still steep (Sri Lanka flat)", fontsize=10)
axs[0].set_ylabel("Under-5 deaths per 1,000"); [a.set_xlabel("Female secondary enrolment (% gross)") for a in axs]; axs[0].legend(frameon=False, fontsize=7)
fig.suptitle("Higher female enrolment goes with lower child mortality, pooled and within countries", x=0.01, ha="left", fontsize=11, fontweight="bold")
fig.tight_layout(rect=(0, 0.03, 1, 0.93)); fig.savefig(FIG / "03_enrolment_vs_u5mr.png", dpi=150)

fig, axs = plt.subplots(1, 2, figsize=(8, 3.4))
axs[0].hist(df.gdp_pc_ppp, bins=20, color="#888"); axs[0].set_title("Before: GDP per capita (skew %.2f)" % skew(df.gdp_pc_ppp), fontsize=9)
axs[1].hist(df.log_gdp, bins=20, color="#01411C"); axs[1].set_title("After: log GDP per capita (skew %.2f)" % skew(df.log_gdp), fontsize=9)
fig.suptitle("Logging GDP per capita pulls in the long right tail", x=0.01, ha="left", fontsize=11, fontweight="bold"); fig.tight_layout(rect=(0, 0, 1, 0.92)); fig.savefig(FIG / "04_log_transform.png", dpi=150)

tr, te = df.index[df.year <= 2015], df.index[df.year > 2015]
rf = RandomForestRegressor(n_estimators=300, random_state=0, min_samples_leaf=2).fit(df.loc[tr, base], df.loc[tr, "u5mr"])
rd = make_pipeline(StandardScaler(), Ridge(alpha=1.0)).fit(df.loc[tr, base], df.loc[tr, "u5mr"])
fig, ax = plt.subplots(figsize=(5, 4.2)); y = df.loc[te, "u5mr"]
ax.scatter(y, rd.predict(df.loc[te, base]), s=14, label="Ridge", color="#01411C"); ax.scatter(y, rf.predict(df.loc[te, base]), s=14, label="Random forest", color="#E07B00")
ax.plot([0, 70], [0, 70], "k--", lw=1); ax.set_xlabel("Actual"); ax.set_ylabel("Predicted"); ax.legend(frameon=False)
ax.set_title("Models predict 2016-23 mortality well when trained on earlier years", loc="left", fontsize=9, fontweight="bold")
fig.tight_layout(); fig.savefig(FIG / "05_prediction_time_split.png", dpi=150)
print("\nfigures saved:", sorted(p.name for p in FIG.iterdir()))
