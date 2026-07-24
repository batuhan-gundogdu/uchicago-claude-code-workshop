"""Per-column description: type, range/levels, and missing counts."""
import pandas as pd

df = pd.read_csv("fitness_cohort.csv")

print("=== missing values by column ===")
miss = df.isna().sum()
print(miss[miss > 0].to_dict() or "none")

print("\n=== per-column detail ===")
for c in df.columns:
    s = df[c]
    if pd.api.types.is_numeric_dtype(s):
        print(f"{c:20s} numeric   range [{s.min():g}, {s.max():g}]  mean {s.mean():.1f}  missing {s.isna().sum()}")
    else:
        levels = list(s.dropna().unique())
        print(f"{c:20s} category  levels {levels}  missing {s.isna().sum()}")
