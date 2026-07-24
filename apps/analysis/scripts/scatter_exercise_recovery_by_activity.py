"""Scatter weekly_exercise_hrs vs recovery_score, colored by activity_level,
with a separate OLS line per group (Simpson's-paradox check)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
import numpy as np
import pandas as pd
from scipy import stats

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
GROUPS = ["sedentary", "moderate", "active"]
COLORS = {"sedentary": "#2a78d6", "moderate": "#eb6834", "active": "#1baf7a"}

df = pd.read_csv("fitness_cohort.csv")

fig, ax = plt.subplots(figsize=(9.4, 5.8), dpi=150)
fig.patch.set_facecolor(SURFACE)
ax.set_facecolor(SURFACE)

results = []
for g in GROUPS:
    d = df.loc[df["activity_level"] == g, ["weekly_exercise_hrs", "recovery_score"]].dropna()
    x, y = d["weekly_exercise_hrs"].values, d["recovery_score"].values
    c = COLORS[g]
    ax.scatter(x, y, s=9, color=c, alpha=0.10, edgecolor="none")
    lr = stats.linregress(x, y)
    xs = np.linspace(x.min(), x.max(), 100)
    ax.plot(xs, lr.intercept + lr.slope * xs, color=c, linewidth=2.6,
            path_effects=[pe.Stroke(linewidth=4.4, foreground=SURFACE), pe.Normal()],
            label=f"{g}: slope {lr.slope:+.3f}, r {lr.rvalue:+.3f}, p {lr.pvalue:.2g}  (n={len(x):,})")
    results.append((g, len(x), lr.slope, lr.rvalue, lr.pvalue))

# overall (pooled) line for contrast
dall = df[["weekly_exercise_hrs", "recovery_score"]].dropna()
lo = stats.linregress(dall["weekly_exercise_hrs"], dall["recovery_score"])
xs = np.linspace(dall["weekly_exercise_hrs"].min(), dall["weekly_exercise_hrs"].max(), 100)
ax.plot(xs, lo.intercept + lo.slope * xs, color=INK_2, linewidth=2, linestyle=(0, (5, 3)),
        label=f"pooled: slope {lo.slope:+.3f}, r {lo.rvalue:+.3f}")

ax.set_title("weekly_exercise_hrs vs recovery_score, by activity level",
             color=INK, fontsize=14, fontweight="bold", loc="left", pad=12)
ax.set_xlabel("weekly_exercise_hrs", color=INK_2, fontsize=11)
ax.set_ylabel("recovery_score", color=INK_2, fontsize=11)
ax.tick_params(colors=INK_2)
for s in ["top", "right"]:
    ax.spines[s].set_visible(False)
for s in ["left", "bottom"]:
    ax.spines[s].set_color("#d8d7d3")
ax.grid(color="#ececea", linewidth=0.8)
ax.set_axisbelow(True)

leg = ax.legend(frameon=True, loc="lower left", fontsize=9, facecolor="white", edgecolor="#d8d7d3")
for t in leg.get_texts():
    t.set_color(INK)

fig.tight_layout()
fig.savefig("plots/scatter_exercise_recovery_by_activity.png", bbox_inches="tight", facecolor=SURFACE)
print("saved plots/scatter_exercise_recovery_by_activity.png")
for g, n, s, r, p in results:
    print(f"  {g:10s} n={n:4d}  slope={s:+.4f}  r={r:+.4f}  p={p:.3g}")
print(f"  {'pooled':10s} n={len(dall):4d}  slope={lo.slope:+.4f}  r={lo.rvalue:+.4f}  p={lo.pvalue:.3g}")
