import pandas as pd, numpy as np, warnings
import matplotlib.pyplot as plt
from pathlib import Path
warnings.filterwarnings("ignore")

CLEAN, CH = Path(r"C:\Users\varsh\Desktop\medgenome_bi_project\data\clean"), Path(r"C:\Users\varsh\Desktop\medgenome_bi_project\docs\charts")
BLUE, ORANGE, GREY = "#2a78d6", "#eb6834", "#c9c8c2"
plt.rcParams.update({"figure.dpi": 110, "savefig.dpi": 200, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "grid.color": "#e6e5e0", "grid.linewidth": .6, "axes.axisbelow": True,
                     "axes.titleweight": "bold", "axes.titlelocation": "left", "axes.titlesize": 12})

# =============== PART A: REVENUE FORECAST ===============
mf = pd.read_csv(CLEAN/"monthly_financials.csv", parse_dates=["Month"]).set_index("Month").asfreq("MS")
y = mf.RevenueINR / 1e5                                   # Rs lakh
H_TEST = 6                                                # hold out last 6 months to test models
train, test = y[:-H_TEST], y[-H_TEST:]

def _idx(s, h): return pd.date_range(s.index[-1] + pd.offsets.MonthBegin(), periods=h, freq="MS")
def mavg(s, h):   return pd.Series(s.iloc[-6:].mean(), index=_idx(s, h))
def snaive(s, h): return pd.Series(s.iloc[-12:].values[:h], index=_idx(s, h))      # same month last year
def lin_trend(s, h):                                                              # straight-line trend
    t = np.arange(len(s)); b1, b0 = np.polyfit(t, s.values, 1)
    return pd.Series(b0 + b1 * np.arange(len(s), len(s) + h), index=_idx(s, h))
def trend_seasonal(s, h):                                                         # trend + average calendar-month effect
    t = np.arange(len(s)); b1, b0 = np.polyfit(t, s.values, 1)
    season = (s - (b0 + b1 * t)).groupby(s.index.month).mean()                    # avg deviation from trend, per month
    idx = _idx(s, h); trend = b0 + b1 * np.arange(len(s), len(s) + h)
    return pd.Series(trend + season.reindex(idx.month).values, index=idx)
models = {"Moving avg (6m)": mavg, "Seasonal naive": snaive, "Linear trend": lin_trend, "Trend + seasonality": trend_seasonal}

rows = []
for name, fn in models.items():
    p = fn(train, H_TEST); p.index = test.index
    rows.append((name, np.mean(abs(test - p)), np.mean(abs((test - p) / test)) * 100))
bt = pd.DataFrame(rows, columns=["Model", "MAE (Rs lakh)", "MAPE %"]).sort_values("MAPE %").round(2)
print("--- Backtest on last 6 months ---\n", bt.to_string(index=False))
best = bt.Model.iloc[0]; print("\nBest model:", best)

# Final forecast: refit on all data, horizon = Nov-26 .. Mar-27 (completes Indian FY27: Apr-26..Mar-27)
H = 5
fc = models[best](y, H)
resid_sd = np.std(test - models[best](train, H_TEST).set_axis(test.index))               # backtest error spread -> interval width
out = pd.DataFrame({"Month": fc.index, "ForecastRevLakh": fc.values, "Lower80": fc.values - 1.28 * resid_sd, "Upper80": fc.values + 1.28 * resid_sd}).round(2)
out.to_csv(CLEAN/"revenue_forecast.csv", index=False); print("\n", out.to_string(index=False))

fy27_actual = y["2026-04":"2026-10"].sum(); fy27_fc = fy27_actual + fc.sum()
fy26 = y["2025-04":"2026-03"].sum()
bud = pd.read_csv(CLEAN/"budgets.csv", parse_dates=["Month"]).set_index("Month").BudgetRevenueINR / 1e5
print(f"\nFY26 actual: {fy26:.0f} lakh | FY27 (7m actual + 5m forecast): {fy27_actual:.0f} + {fc.sum():.0f} = {fy27_fc:.0f} lakh ({fy27_fc/fy26-1:+.1%} vs FY26)")
print(f"FY27 YTD actual vs budget (Apr-Oct 26): {fy27_actual:.0f} vs {bud['2026-04':'2026-10'].sum():.0f} lakh ({fy27_actual/bud['2026-04':'2026-10'].sum()-1:+.1%})")

fig, ax = plt.subplots(figsize=(9.5, 4))
ax.plot(y.index, y, color=GREY, lw=1.8, label="Actual"); ax.plot(fc.index, fc, color=BLUE, lw=2.2, marker="o", ms=4, label=f"Forecast ({best})")
ax.fill_between(out.Month, out.Lower80, out.Upper80, color=BLUE, alpha=.15, label="80% range")
ax.set(title="Revenue outlook to end of FY27: broadly flat", ylabel="Rs lakh"); ax.legend(frameon=False, loc="lower left")
ax.text(1, -.16, "Synthetic data - not MedGenome data", transform=ax.transAxes, ha="right", fontsize=8, color="#8a8984")
fig.tight_layout(); fig.savefig(CH/"09_forecast.png"); plt.close(fig)

# =============== PART B: M&A TARGET SCREENING ===============
ma = pd.read_csv(CLEAN/"ma_targets.csv"); cen = pd.read_csv(CLEAN/"dim_centres.csv"); mk = pd.read_csv(CLEAN/"market_estimates.csv")
ma["Revenue_Cr"] = ma.AnnualRevenueINR / 1e7; ma["EBITDA_Cr"] = ma.EBITDAINR / 1e7
ma = ma.merge(cen[["City", "State"]].drop_duplicates(), on="City", how="left").merge(mk[["State", "EstimatedCurrentPenetration", "AssumedAnnualMarketGrowth"]], on="State", how="left")

def minmax(s): return (s - s.min()) / (s.max() - s.min())
ma["MarginScore"] = minmax(ma.EBITDAMargin) * 4 + 1          # put financials on same 1-5 scale as the fit scores
ma["GrowthScore"] = minmax(ma.AssumedAnnualMarketGrowth) * 4 + 1
W_BASE = {"StrategicFitScore_1to5": .30, "CapabilityFitScore_1to5": .25, "GeographicFitScore_1to5": .15, "MarginScore": .20, "GrowthScore": .10}
W_ALT  = {"StrategicFitScore_1to5": .20, "CapabilityFitScore_1to5": .20, "GeographicFitScore_1to5": .20, "MarginScore": .30, "GrowthScore": .10}   # finance-led view
def score(w): return sum(ma[c] * v for c, v in w.items())
ma["WeightedScore"] = score(W_BASE).round(2); ma["Rank"] = ma.WeightedScore.rank(ascending=False).astype(int)
ma["Rank_FinanceLed"] = score(W_ALT).rank(ascending=False).astype(int)

# Illustrative valuation: ASSUMPTION - 10x to 14x EBITDA (replace with cited comparables in real work)
ma["EV_Low_Cr"], ma["EV_High_Cr"] = (ma.EBITDA_Cr * 10).round(1), (ma.EBITDA_Cr * 14).round(1)
ma["TargetRevenue_vs_OurRevenue"] = (ma.AnnualRevenueINR / (mf.RevenueINR["2025-11":"2026-10"].sum())).round(1)   # trailing-12-month
cols = ["Rank", "TargetCompany", "City", "Specialisation", "Revenue_Cr", "EBITDA_Cr", "EBITDAMargin", "WeightedScore", "Rank_FinanceLed", "EV_Low_Cr", "EV_High_Cr", "TargetRevenue_vs_OurRevenue"]
res = ma.sort_values("Rank")[cols]; res.to_csv(CLEAN/"ma_target_ranking.csv", index=False)
print("\n--- M&A screening ---\n", res.to_string(index=False))
print("\nMedGenome-style check: our TTM revenue = Rs %.2f cr" % (mf.RevenueINR["2025-11":"2026-10"].sum() / 1e7))