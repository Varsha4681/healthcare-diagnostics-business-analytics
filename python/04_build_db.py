import sqlite3, pandas as pd
from pathlib import Path
CLEAN, SQL = Path(r"C:\Users\varsh\Desktop\medgenome_bi_project\data\clean"), Path(r"C:\Users\varsh\Desktop\medgenome_bi_project\sql")
con = sqlite3.connect(SQL/"diagnostics.db")
con.executescript((SQL/"01_schema.sql").read_text())

f = pd.read_csv(CLEAN/"fact_transactions.csv", parse_dates=["OrderDate", "YearMonth"])
f["OrderDate"] = f.OrderDate.dt.strftime("%Y-%m-%d"); f["YearMonth"] = f.YearMonth.dt.strftime("%Y-%m-%d")
pd.read_csv(CLEAN/"dim_centres.csv").to_sql("dim_centres", con, if_exists="append", index=False)
pd.read_csv(CLEAN/"dim_tests.csv").to_sql("dim_tests", con, if_exists="append", index=False)
f.to_sql("fact_transactions", con, if_exists="append", index=False)

for name in ["monthly_financials", "budgets", "market_estimates", "competitors", "ma_targets"]:
    d = pd.read_csv(CLEAN/f"{name}.csv")
    if "Month" in d: d["Month"] = pd.to_datetime(d.Month).dt.strftime("%Y-%m-%d")
    d.to_sql(name, con, if_exists="replace", index=False)

for t in ["fact_transactions", "dim_centres", "dim_tests", "monthly_financials", "budgets", "market_estimates", "competitors", "ma_targets"]:
    print(f"{t:20s}", con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0], "rows")
print("FK violations:", con.execute("PRAGMA foreign_key_check").fetchall())
con.close()