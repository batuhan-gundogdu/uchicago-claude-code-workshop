"""biomarker_x distribution split by activity_level: overlaid KDEs + group means."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
# ordinal order -> fixed categorical hues (blue, orange, aqua)
GROUPS = ["sedentary", "moderate", "active"]
COLORS = {"sedentary": "#2a78d6", "moderate": "#eb6834", "active": "#1baf7a"}

df = pd.read_csv("fitness_cohort.csv")

fig, ax = plt.subplots(figsize=(9.2, 5.4), dpi=150)
fig.patch.set_facecolor(SURFACE)
ax.set_facecolor(SURFACE)

# shared grid across all groups
x_all = df["biomarker_x"].dropna()
grid = np.linspace(x_all.min(), x_all.max(), 400)

stats = []
for g in GROUPS:
    x = df.loc[df["activity_level"] == g, "biomarker_x"].dropna().values
    bw = 1.06 * x.std() * len(x) ** (-1 / 5)  # Silverman
    kde = np.exp(-0.5 * ((grid[:, None] - x[None, :]) / bw) ** 2).sum(1)
    kde /= (len(x) * bw * np.sqrt(2 * np.pi))
    c = COLORS[g]
    ax.fill_between(grid, kde, color=c, alpha=0.18, linewidth=0)
    ax.plot(grid, kde, color=c, linewidth=2, label=f"{g}  (n={len(x):,})")
    ax.axvline(x.mean(), color=c, linewidth=1.1, linestyle="--", alpha=0.9)
    stats.append((g, len(x), x.mean(), x.std()))

# direct-label each mean at the top (satisfies relief rule for the low-contrast hue)
top = ax.get_ylim()[1]
for i, (g, n, m, sd) in enumerate(stats):
    ax.annotate(f"{g} mean {m:.1f}", xy=(m, top * (0.97 - 0.07 * i)),
                xytext=(6, 0), textcoords="offset points",
                color=COLORS[g], fontsize=9, fontweight="bold", va="top")

ax.set_title("biomarker_x by activity level", color=INK, fontsize=14, fontweight="bold", loc="left", pad=12)
ax.set_xlabel("biomarker_x", color=INK_2, fontsize=11)
ax.set_ylabel("density", color=INK_2, fontsize=11)
ax.tick_params(colors=INK_2)
for s in ["top", "right"]:
    ax.spines[s].set_visible(False)
for s in ["left", "bottom"]:
    ax.spines[s].set_color("#d8d7d3")
ax.grid(axis="y", color="#ececea", linewidth=0.8)
ax.set_axisbelow(True)

leg = ax.legend(frameon=False, loc="upper left", fontsize=10, title="activity_level")
leg.get_title().set_color(INK_2)
for t in leg.get_texts():
    t.set_color(INK)

fig.tight_layout()
fig.savefig("plots/dist_biomarker_x_by_activity.png", bbox_inches="tight", facecolor=SURFACE)
print("saved plots/dist_biomarker_x_by_activity.png")
for g, n, m, sd in stats:
    print(f"  {g:10s} n={n:4d}  mean={m:.2f}  std={sd:.2f}")
