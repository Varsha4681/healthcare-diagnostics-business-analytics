import pandas as pd
from pathlib import Path

RAW = Path(r"C:\Users\varsh\Desktop\medgenome_bi_project\data\raw\Healthcare_Diagnostics_Practice_Dataset.xlsx")
OUT = Path(r"C:\Users\varsh\Desktop\medgenome_bi_project\data\raw\csv"); OUT.mkdir(exist_ok=True)

sheets = pd.read_excel(RAW, sheet_name=None)
for name, df in sheets.items():
    if name == "Read_Me":
        continue
    fname = name.replace("&", "").lower() + ".csv"   # M&A_Targets -> ma_targets.csv
    df.to_csv(OUT / fname, index=False)
    print(f"{name:20s} {df.shape} -> {fname}")