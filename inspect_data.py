"""
Dataset Inspector - run this once to see the real column names
and a sample row before building the Review Summarizer Agent.

Run:  python inspect_data.py
"""

import pandas as pd

CSV_PATH = "archive/1429_1.csv"

df = pd.read_csv(CSV_PATH)

print("COLUMNS:")
for col in df.columns:
    print(f"  - {col}")

print(f"\nTotal rows: {len(df)}")

print("\nSAMPLE ROW:")
print(df.iloc[0].to_dict())

print("\nUNIQUE PRODUCT NAMES (first 10):")
# try common column name variants
name_col = None
for candidate in ["name", "product_name", "asins", "title"]:
    if candidate in df.columns:
        name_col = candidate
        break

if name_col:
    print(df[name_col].dropna().unique()[:10])
else:
    print("Could not auto-detect product name column - check COLUMNS list above.")
