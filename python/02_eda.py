import pandas as pd, numpy as np
import matplotlib.pyplot as plt, seaborn as sns
from scipy import stats
from pathlib import Path

CLEAN, OUT = Path(r"C:\Users\varsh\Desktop\medgenome_bi_project\data\clean"), Path(r"C:\Users\varsh\Desktop\medgenome_bi_project\docs\charts"); OUT.mkdir(parents=True, exist_ok=True)
BLUE, ORANGE, GREY, INK = "#2a78d6", "#eb6834", "#c9c8c2", "#0b0b0b"
plt.rcParams.update({"figure.dpi": 110, "savefig.dpi": 200, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.edgecolor": "#8a8984", "axes.grid": True, "grid.color": "#e6e5e0", "grid.linewidth": .6,
                     "axes.axisbelow": True, "font.size": 10, "axes.titlesize": 12, "axes.titleweight": "bold",
                     "axes.titlelocation": "left"})
def save(name, fig): fig.tight_layout(); fig.savefig(OUT/f"{name}.png"); plt.close(fig)
FOOT = "Synthetic data - not MedGenome data"

# ---------- load & join ----------
f = pd.read_csv(CLEAN/"fact_transactions.csv", parse_dates=["OrderDate", "YearMonth"])
f = f.merge(pd.read_csv(CLEAN/"dim_centres.csv"), on="CentreID") \
     .merge(pd.read_csv(CLEAN/"dim_tests.csv")[["TestID", "TestName", "Category"]], on="TestID")
k = f[f.IsCompleted == 1].copy()          # revenue/margin analysis = completed orders only
def summ(by): 
    g = k.groupby(by).agg(Orders=("OrderID", "count"), Revenue=("RevenueINR", "sum"), GP=("GrossProfitINR", "sum"),
                          AvgDisc=("DiscountRate", "mean"), TATBreach=("TATBreachFlag", "mean"))
    g["GM%"] = g.GP / g.Revenue; g["AvgOrderValue"] = g.Revenue / g.Orders; return g

# ================= 1. DESCRIPTIVE =================
print("KPIs: revenue %.2f cr | GP %.2f cr | GM %.1f%% | AOV Rs %.0f | discounted orders %.0f%%" %
      (k.RevenueINR.sum()/1e7, k.GrossProfitINR.sum()/1e7, 100*k.GrossProfitINR.sum()/k.RevenueINR.sum(),
       k.RevenueINR.mean(), 100*(k.DiscountRate > 0).mean()))
print("Discount given away: Rs %.1f lakh" % (k.DiscountINR.sum()/1e5))
print(k[["RevenueINR", "DirectCostINR", "TurnaroundHours", "DiscountRate"]].describe().round(1).to_string())

# ================= 2. CHARTS =================
# 1. Monthly trend (calendar-month seasonality uses AVERAGE per month: Nov/Dec only have 2 years of data)
m = k.groupby("YearMonth").RevenueINR.sum() / 1e5
fig, ax = plt.subplots(figsize=(9, 3.8))
ax.plot(m.index, m, color=GREY, lw=1.5, label="Monthly revenue"); ax.plot(m.index, m.rolling(3).mean(), color=BLUE, lw=2.2, label="3-month average")
ax.set(title="Revenue is range-bound at Rs 19-28 lakh a month, with no clear growth", ylabel="Rs lakh"); ax.legend(frameon=False, loc="lower left")
ax.text(1, -.18, FOOT, transform=ax.transAxes, ha="right", fontsize=8, color="#8a8984"); save("01_monthly_revenue", fig)
seas = m.groupby(m.index.month).mean().round(1)
print("\nAvg monthly revenue by calendar month (Rs lakh):", seas.to_dict())

# 2. Test performance
t = summ("TestName").sort_values("Revenue")
fig, ax = plt.subplots(figsize=(8, 4.2)); ax.barh(t.index, t.Revenue/1e5, color=BLUE, height=.6)
for i, (rev, gm, n) in enumerate(zip(t.Revenue, t["GM%"], t.Orders)): ax.text(rev/1e5 + 1, i, f"{gm:.0%} GM | {n} orders", va="center", fontsize=8.5)
ax.set(title="Whole Exome Sequencing leads revenue; Thalassemia is high-margin but small", xlabel="Revenue (Rs lakh)", xlim=(0, t.Revenue.max()/1e5*1.35)); ax.grid(axis="y", visible=False); save("02_test_performance", fig)

# 3. Centre performance
c = summ("CentreName").sort_values("Revenue")
fig, ax = plt.subplots(figsize=(8, 4.6)); ax.barh(c.index, c.Revenue/1e5, color=BLUE, height=.6)
for i, (rev, gm) in enumerate(zip(c.Revenue, c["GM%"])): ax.text(rev/1e5 + .6, i, f"{gm:.1%} GM", va="center", fontsize=8.5)
ax.set(title="Centre revenue differences are about volume - margins are almost identical", xlabel="Revenue (Rs lakh)", xlim=(0, c.Revenue.max()/1e5*1.2)); ax.grid(axis="y", visible=False); save("03_centre_revenue", fig)

# 4. Discount vs margin
d = summ("DiscountRate")
fig, ax = plt.subplots(figsize=(6.5, 3.8)); bars = ax.bar([f"{x:.0%}" for x in d.index], d["GM%"]*100, color=[GREY, BLUE, BLUE, ORANGE], width=.55)
for b, v, n in zip(bars, d["GM%"], d.Orders): ax.text(b.get_x()+b.get_width()/2, v*100+.6, f"{v:.1%}\n(n={n})", ha="center", fontsize=9)
ax.set(title="Every 5pp of discount costs ~2pp of gross margin", xlabel="Discount rate", ylabel="Gross margin %", ylim=(0, 75)); ax.grid(axis="x", visible=False); save("04_discount_vs_margin", fig)

# 5. TAT vs target, by test (ratio, so tests are comparable)
order = k.groupby("TestName").TATRatio.median().sort_values().index
fig, ax = plt.subplots(figsize=(8.5, 4.4)); sns.boxplot(data=k, y="TestName", x="TATRatio", order=order, color="#b9d3f2", linecolor=BLUE, fliersize=2, ax=ax)
ax.axvline(1, color=ORANGE, lw=1.8); ax.text(1.02, -.45, "target", color=ORANGE, fontsize=9)
ax.set(title="Median order sits right at target - half of all orders breach it", xlabel="Actual TAT / target TAT", ylabel=""); ax.grid(axis="y", visible=False); save("05_tat_by_test", fig)

# 6. Breach & failure by centre (two panels, one axis each)
cc = f.groupby("CentreName").agg(breach=("TATBreachFlag", lambda s: s[f.loc[s.index, "IsCompleted"] == 1].mean()), fail=("IsCompleted", lambda s: 1-s.mean())).sort_values("breach")
fig, axs = plt.subplots(1, 2, figsize=(11, 4.4), sharey=True)
for ax, col, ttl in zip(axs, ["breach", "fail"], ["TAT breach rate (completed orders)", "Failed-order rate (cancelled + rejected)"]):
    ax.barh(cc.index, cc[col]*100, color=BLUE, height=.6); ax.axvline((f.IsCompleted.eq(0).mean() if col == "fail" else k.TATBreachFlag.mean())*100, color=ORANGE, lw=1.6)
    ax.set_title(ttl); ax.set_xlabel("%"); ax.grid(axis="y", visible=False)
axs[0].text(0.5, -.2, "Orange line = company average", transform=axs[0].transAxes, fontsize=8, color=ORANGE); save("06_centre_ops", fig)

# 7. Channel
ch = summ("ReferralChannel").sort_values("Revenue", ascending=False)
fig, ax = plt.subplots(figsize=(6.5, 3.6)); ax.bar(ch.index, ch.Revenue/1e5, color=BLUE, width=.55)
for i, (r, a) in enumerate(zip(ch.Revenue, ch.AvgOrderValue)): ax.text(i, r/1e5+4, f"Rs {a:,.0f}/order", ha="center", fontsize=8.5)
ax.set(title="Hospitals and physicians drive ~65% of revenue", ylabel="Revenue (Rs lakh)", ylim=(0, 340)); ax.grid(axis="x", visible=False); save("07_channel_revenue", fig)

# 8. Correlation heatmap
num = k[["RevenueINR", "DirectCostINR", "GrossMarginPct", "DiscountRate", "TurnaroundHours", "TATRatio"]]
fig, ax = plt.subplots(figsize=(6, 4.8)); sns.heatmap(num.corr(method="spearman"), annot=True, fmt=".2f", cmap=sns.diverging_palette(250, 30, as_cmap=True), center=0, vmin=-1, vmax=1, cbar=False, ax=ax)
ax.set_title("Spearman correlations (completed orders)"); save("08_correlation", fig)

# ================= 3. STATISTICAL TESTS =================
print("\n--- Hypothesis tests (alpha = 0.05) ---")
rho, p = stats.spearmanr(k.DiscountRate, k.GrossMarginPct); print(f"Discount vs gross margin: rho={rho:.2f}, p={p:.1e} -> SIGNIFICANT, moderate negative")
for col in ["CentreName", "TestName", "ReferralChannel"]:
    h, p = stats.kruskal(*[g.TATRatio for _, g in k.groupby(col)]); print(f"TAT ratio differs by {col:16s}: p={p:.3f} -> {'significant' if p < .05 else 'NOT significant'}")
for col in ["CentreName", "ReferralChannel", "TestName"]:
    chi, p, *_ = stats.chi2_contingency(pd.crosstab(f[col], f.IsCompleted)); print(f"Order failure differs by {col:16s}: p={p:.3f} -> {'significant' if p < .05 else 'NOT significant'}")
h, p = stats.kruskal(*[g.DiscountRate for _, g in k.groupby("ReferralChannel")]); print(f"Discount level differs by channel : p={p:.3f}")
print("\nBreach rate by year:", k.groupby(k.OrderDate.dt.year).TATBreachFlag.mean().round(3).to_dict())
print("\nTop-3 test revenue share: %.0f%%" % (100*summ("TestName").Revenue.nlargest(3).sum()/k.RevenueINR.sum()))
print("Top-5 centre revenue share: %.0f%%" % (100*summ("CentreName").Revenue.nlargest(5).sum()/k.RevenueINR.sum()))
