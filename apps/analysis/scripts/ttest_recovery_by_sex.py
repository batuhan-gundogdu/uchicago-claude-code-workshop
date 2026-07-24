"""Welch's t-test of recovery_score between the two sex groups, with Cohen's d."""
import numpy as np
import pandas as pd
from scipy import stats

df = pd.read_csv("fitness_cohort.csv")
a = df.loc[df["sex"] == "M", "recovery_score"].dropna().values
b = df.loc[df["sex"] == "F", "recovery_score"].dropna().values

t, p = stats.ttest_ind(a, b, equal_var=False)  # Welch

# Cohen's d with pooled SD
na, nb = len(a), len(b)
sp = np.sqrt(((na - 1) * a.var(ddof=1) + (nb - 1) * b.var(ddof=1)) / (na + nb - 2))
d = (a.mean() - b.mean()) / sp
# 95% CI on the mean difference (Welch)
diff = a.mean() - b.mean()
se = np.sqrt(a.var(ddof=1) / na + b.var(ddof=1) / nb)
df_w = se**4 / ((a.var(ddof=1)/na)**2 / (na-1) + (b.var(ddof=1)/nb)**2 / (nb-1))
tcrit = stats.t.ppf(0.975, df_w)
ci = (diff - tcrit * se, diff + tcrit * se)

print(f"M: n={na}  mean={a.mean():.3f}  sd={a.std(ddof=1):.3f}")
print(f"F: n={nb}  mean={b.mean():.3f}  sd={b.std(ddof=1):.3f}")
print(f"mean diff (M - F) = {diff:+.3f}   95% CI [{ci[0]:+.3f}, {ci[1]:+.3f}]")
print(f"Welch t({df_w:.0f}) = {t:.3f}   p = {p:.4g}")
print(f"Cohen's d = {d:+.4f}")
