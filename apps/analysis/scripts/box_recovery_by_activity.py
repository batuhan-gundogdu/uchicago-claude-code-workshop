"""Box plot of recovery_score by activity_level."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
GROUPS = ["sedentary", "moderate", "active"]
COLORS = {"sedentary": "#2a78d6", "moderate": "#eb6834", "active": "#1baf7a"}

df = pd.read_csv("fitness_cohort.csv")
data = [df.loc[df["activity_level"] == g, "recovery_score"].dropna().values for g in GROUPS]

fig, ax = plt.subplots(figsize=(8.4, 5.4), dpi=150)
fig.patch.set_facecolor(SURFACE)
ax.set_facecolor(SURFACE)

positions = range(1, len(GROUPS) + 1)
bp = ax.boxplot(data, positions=positions, widths=0.55, patch_artist=True,
                showmeans=True, meanprops=dict(marker="D", markerfacecolor="white",
                markeredgecolor=INK, markersize=6, markeredgewidth=1.2),
                medianprops=dict(color=INK, linewidth=1.6),
                whiskerprops=dict(color=INK_2, linewidth=1.2),
                capprops=dict(color=INK_2, linewidth=1.2),
                flierprops=dict(marker="o", markersize=3, markerfacecolor=INK_2,
                                markeredgecolor="none", alpha=0.25))
for patch, g in zip(bp["boxes"], GROUPS):
    patch.set_facecolor(COLORS[g])
    patch.set_alpha(0.30)
    patch.set_edgecolor(COLORS[g])
    patch.set_linewidth(1.8)

# annotate mean + median above each box
top = max(d.max() for d in data)
for pos, g, d in zip(positions, GROUPS, data):
    ax.annotate(f"mean {d.mean():.1f}\nmed {np.median(d):.1f}\nn={len(d):,}",
                xy=(pos, top + 1.5), ha="center", va="bottom",
                color=COLORS[g], fontsize=9, fontweight="bold")

ax.set_title("recovery_score by activity level", color=INK, fontsize=14, fontweight="bold", loc="left", pad=12)
ax.set_xticks(list(positions))
ax.set_xticklabels(GROUPS, color=INK, fontsize=11)
ax.set_ylabel("recovery_score", color=INK_2, fontsize=11)
ax.set_xlabel("activity_level", color=INK_2, fontsize=11)
ax.tick_params(colors=INK_2)
ax.set_ylim(top=top + 8)
for s in ["top", "right"]:
    ax.spines[s].set_visible(False)
for s in ["left", "bottom"]:
    ax.spines[s].set_color("#d8d7d3")
ax.grid(axis="y", color="#ececea", linewidth=0.8)
ax.set_axisbelow(True)
fig.text(0.125, -0.01, "box = IQR, line = median, white diamond = mean, whiskers = 1.5xIQR",
         color=INK_2, fontsize=8.5)

fig.tight_layout()
fig.savefig("plots/box_recovery_by_activity.png", bbox_inches="tight", facecolor=SURFACE)
print("saved plots/box_recovery_by_activity.png")
for g, d in zip(GROUPS, data):
    q1, med, q3 = np.percentile(d, [25, 50, 75])
    print(f"  {g:10s} n={len(d):4d}  mean={d.mean():.2f}  median={med:.1f}  IQR=[{q1:.1f},{q3:.1f}]")
