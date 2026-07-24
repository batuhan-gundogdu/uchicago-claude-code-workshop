"""Quick baseline profile of the fitness cohort dataset."""
import pandas as pd

df = pd.read_csv("fitness_cohort.csv")

print(f"rows={len(df)}  cols={df.shape[1]}")
print(f"duplicate participant_ids: {df.participant_id.duplicated().sum()}")
print(f"missing values total: {int(df.isna().sum().sum())}")
print("\n--- numeric summary ---")
num = df.select_dtypes("number")
print(num.describe().round(2).T[["mean", "std", "min", "50%", "max"]])
print("\n--- categoricals ---")
for c in ["sex", "cohort", "region", "activity_level", "device_gen"]:
    counts = df[c].value_counts().to_dict()
    print(f"{c}: {counts}")
