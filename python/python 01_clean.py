import pandas as pd, numpy as np
from pathlib import Path

RAW, CLEAN = Path(r"C:\Users\varsh\Desktop\medgenome_bi_project\data\raw\csv"), Path(r"C:\Users\varsh\Desktop\medgenome_bi_project\data\clean")
CLEAN.mkdir(exist_ok=True)

tx = pd.read_csv(RAW/"transactions.csv", parse_dates=["OrderDate"])
centres = pd.read_csv(RAW/"centres.csv")
tests = pd.read_csv(RAW/"tests.csv")
log = []                                   # (check, result, action)
def note(check, result, action): log.append((check, result, action)); print(f"{check:45s} {result!s:>10}  -> {action}")

# ---------- 1. STRUCTURE ----------
note("Rows", len(tx), "expected 5,200")
note("Null cells", int(tx.isna().sum().sum()), "none to treat")
note("Fully duplicated rows", int(tx.duplicated().sum()), "none to drop")
note("Duplicate OrderIDs", int(tx.OrderID.duplicated().sum()), "none to drop")
note("Date range", f"{tx.OrderDate.min():%b-%y}..{tx.OrderDate.max():%b-%y}", "OK")
rep = tx.ClientID.duplicated(keep=False).sum()
note("Orders from repeat ClientIDs", int(rep), "legitimate repeat clients - keep")

# ---------- 2. REFERENTIAL INTEGRITY ----------
note("CentreIDs not in Centres", int((~tx.CentreID.isin(centres.CentreID)).sum()), "FK OK")
note("TestIDs not in Tests", int((~tx.TestID.isin(tests.TestID)).sum()), "FK OK")

# ---------- 3. BUSINESS RULES ----------
nz = tx[tx.OrderStatus != "Completed"]
note("Non-completed orders", len(nz), "keep in fact table, flag IsCompleted=0")
note("Non-completed with revenue > 0", int((nz.RevenueINR > 0).sum()), "rule holds")
note("Rejected status vs SampleRejectedFlag mismatch",
     int(((tx.OrderStatus == "Rejected") != (tx.SampleRejectedFlag == 1)).sum()), "consistent")

df = tx.merge(tests.rename(columns={"DirectCostINR": "StdCostINR"}), on="TestID", how="left") \
       .merge(centres, on="CentreID", how="left")
comp = df.OrderStatus == "Completed"
exp_rev = df.ListPriceINR * (1 - df.DiscountRate)
note("Completed: revenue != list*(1-discount)", int((abs(exp_rev - df.RevenueINR)[comp] > 1).sum()), "pricing logic reconciles")
note("Completed: cost outside 0.5x-1.5x std cost",
     int(((df.DirectCostINR / df.StdCostINR)[comp].pipe(lambda r: (r < .5) | (r > 1.5))).sum()), "cost within normal band")

# ---------- 4. OUTLIERS (flag, never silently drop) ----------
df["TATRatio"] = df.TurnaroundHours / df.TargetTATHours          # normalise: 100h is fine for WES, awful for thalassemia
q1, q3 = df.TATRatio.quantile([.25, .75]); upper = q3 + 1.5 * (q3 - q1)
df["TATOutlierFlag"] = (df.TATRatio > upper).astype(int)
note("TAT outliers (IQR on TAT/target)", int(df.TATOutlierFlag.sum()), f"flagged; threshold ratio={upper:.2f}")
df["TATBreachFlag"] = (df.TurnaroundHours > df.TargetTATHours).astype(int)
note("TAT breaches vs target", f"{df.TATBreachFlag.mean():.1%}", "KPI, not an error")

# ---------- 5. DERIVED COLUMNS ----------
df["IsCompleted"] = comp.astype(int)
df["YearMonth"] = df.OrderDate.dt.to_period("M").dt.to_timestamp()
df["DiscountINR"] = np.where(comp, df.ListPriceINR - df.RevenueINR, 0)
df["GrossProfitINR"] = df.RevenueINR - df.DirectCostINR          # negative on non-completed = lost cost
df["GrossMarginPct"] = np.where(comp, df.GrossProfitINR / df.RevenueINR, np.nan)

fact = df[["OrderID","OrderDate","YearMonth","CentreID","TestID","ClientID","ReferralChannel","OrderStatus",
           "IsCompleted","DiscountRate","DiscountINR","RevenueINR","DirectCostINR","GrossProfitINR","GrossMarginPct",
           "TurnaroundHours","TargetTATHours","TATRatio","TATBreachFlag","TATOutlierFlag","SampleRejectedFlag"]]
fact.to_csv(CLEAN/"fact_transactions.csv", index=False)
pd.read_csv(RAW/"centres.csv").to_csv(CLEAN/"dim_centres.csv", index=False)
tests.to_csv(CLEAN/"dim_tests.csv", index=False)
for f in ["monthly_financials","budgets","market_estimates","competitors","ma_targets"]:
    pd.read_csv(RAW/f"{f}.csv").to_csv(CLEAN/f"{f}.csv", index=False)

pd.DataFrame(log, columns=["Check","Result","Action"]).to_csv(CLEAN/"data_quality_log.csv", index=False)

# ---------- 6. SANITY: tie back to Monthly_Financials ----------
mf = pd.read_csv(RAW/"monthly_financials.csv")
print("\nRevenue tie-out:", fact.RevenueINR.sum() == mf.RevenueINR.sum(),
      "| Direct cost tie-out:", round(fact.DirectCostINR.sum(),2) == round(mf.DirectCostsINR.sum(),2))
print("Completed gross margin: %.1f%%" % (100*fact[fact.IsCompleted==1].GrossProfitINR.sum()/fact.RevenueINR.sum()))
print("Cost of failed orders (INR):", int(fact[fact.IsCompleted==0].DirectCostINR.sum()))