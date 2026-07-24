"""Scatter of weekly_exercise_hrs vs recovery_score with OLS regression line."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
BLUE = "#2a78d6"
RED = "#e34948"

df = pd.read_csv("fitness_cohort.csv")
d = df[["weekly_exercise_hrs", "recovery_score"]].dropna()
x = d["weekly_exercise_hrs"].values
y = d["recovery_score"].values

lr = stats.linregress(x, y)
xs = np.linspace(x.min(), x.max(), 200)
ys = lr.intercept + lr.slope * xs
# 95% CI band for the mean line
n = len(x)
resid_se = np.sqrt(((y - (lr.intercept + lr.slope * x)) ** 2).sum() / (n - 2))
xbar = x.mean()
ssx = ((x - xbar) ** 2).sum()
se_line = resid_se * np.sqrt(1 / n + (xs - xbar) ** 2 / ssx)
tcrit = stats.t.ppf(0.975, n - 2)

fig, ax = plt.subplots(figsize=(9, 5.6), dpi=150)
fig.patch.set_facecolor(SURFACE)
ax.set_facecolor(SURFACE)

ax.scatter(x, y, s=9, color=BLUE, alpha=0.12, edgecolor="none")
ax.fill_between(xs, ys - tcrit * se_line, ys + tcrit * se_line, color=RED, alpha=0.18, linewidth=0)
ax.plot(xs, ys, color=RED, linewidth=2.2)

sign = "+" if lr.intercept >= 0 else "-"
txt = (f"recovery = {lr.slope:.3f}xexercise {sign} {abs(lr.intercept):.1f}\n"
       f"r = {lr.rvalue:.3f}   r2 = {lr.rvalue**2:.3f}\n"
       f"p = {lr.pvalue:.3g}   n = {n:,}")
ax.text(0.98, 0.97, txt, transform=ax.transAxes, ha="right", va="top",
        fontsize=10, color=INK, family="monospace",
        bbox=dict(boxstyle="round,pad=0.5", facecolor="white", edgecolor="#d8d7d3"))

ax.set_title("weekly_exercise_hrs vs recovery_score", color=INK, fontsize=14, fontweight="bold", loc="left", pad=12)
ax.set_xlabel("weekly_exercise_hrs", color=INK_2, fontsize=11)
ax.set_ylabel("recovery_score", color=INK_2, fontsize=11)
ax.tick_params(colors=INK_2)
for s in ["top", "right"]:
    ax.spines[s].set_visible(False)
for s in ["left", "bottom"]:
    ax.spines[s].set_color("#d8d7d3")
ax.grid(color="#ececea", linewidth=0.8)
ax.set_axisbelow(True)

fig.tight_layout()
fig.savefig("plots/scatter_exercise_recovery.png", bbox_inches="tight", facecolor=SURFACE)
print("saved plots/scatter_exercise_recovery.png")
print(f"slope={lr.slope:.4f}  intercept={lr.intercept:.3f}  r={lr.rvalue:.4f}  r2={lr.rvalue**2:.4f}  p={lr.pvalue:.4g}  n={n}")
