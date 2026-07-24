"""Distribution of biomarker_x: histogram + KDE, mean/median marked."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# ---- palette (from dataviz reference, light surface) ----
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
BLUE = "#2a78d6"

df = pd.read_csv("fitness_cohort.csv")
x = df["biomarker_x"].dropna()

fig, ax = plt.subplots(figsize=(9, 5.2), dpi=150)
fig.patch.set_facecolor(SURFACE)
ax.set_facecolor(SURFACE)

# histogram (density) + KDE overlay
bins = np.histogram_bin_edges(x, bins="fd")
ax.hist(x, bins=bins, density=True, color=BLUE, alpha=0.55, edgecolor=SURFACE, linewidth=0.6)

# KDE via gaussian smoothing (numpy only, no scipy dependency)
grid = np.linspace(x.min(), x.max(), 400)
bw = 1.06 * x.std() * len(x) ** (-1 / 5)  # Silverman's rule
kde = np.exp(-0.5 * ((grid[:, None] - x.values[None, :]) / bw) ** 2).sum(1)
kde /= (len(x) * bw * np.sqrt(2 * np.pi))
ax.plot(grid, kde, color=BLUE, linewidth=2)

# mean & median reference lines (stagger labels so near-equal values don't collide)
mean, median = x.mean(), x.median()
top = ax.get_ylim()[1]
for val, style, label, yfrac in [(mean, "-", "mean", 0.95), (median, "--", "median", 0.86)]:
    ax.axvline(val, color=INK_2, linewidth=1.2, linestyle=style)
    ax.annotate(f"{label} {val:.1f}", xy=(val, top * yfrac),
                xytext=(6, 0), textcoords="offset points",
                color=INK_2, fontsize=9, va="top")

# chrome
ax.set_title("Distribution of biomarker_x", color=INK, fontsize=14, fontweight="bold", loc="left", pad=12)
ax.set_xlabel("biomarker_x", color=INK_2, fontsize=11)
ax.set_ylabel("density", color=INK_2, fontsize=11)
ax.tick_params(colors=INK_2)
for spine in ["top", "right"]:
    ax.spines[spine].set_visible(False)
for spine in ["left", "bottom"]:
    ax.spines[spine].set_color("#d8d7d3")
ax.grid(axis="y", color="#ececea", linewidth=0.8)
ax.set_axisbelow(True)

# caption with n / skew
n = len(x)
n_missing = int(df["biomarker_x"].isna().sum())
miss_note = "no missing" if n_missing == 0 else f"{n_missing} missing excluded"
skew = x.skew()
fig.text(0.125, -0.01, f"n = {n:,}  ({miss_note})   |   std = {x.std():.1f}   skew = {skew:+.2f}",
         color=INK_2, fontsize=9)

fig.tight_layout()
fig.savefig("plots/dist_biomarker_x.png", bbox_inches="tight", facecolor=SURFACE)
print(f"saved plots/dist_biomarker_x.png  |  n={n}  mean={mean:.2f}  median={median:.2f}  std={x.std():.2f}  skew={skew:+.3f}  range=[{x.min():.1f},{x.max():.1f}]")
