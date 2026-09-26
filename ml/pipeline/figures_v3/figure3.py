"""Figure 3. What the evaluation protocol controls, and how much a single
composition-grouped split can move the reported score.

Inputs : figure3_protocols.csv, figure3_repeats.csv
Outputs: figure3.png (600 dpi), figure3.pdf, figure3.svg
"""
import numpy as np
import pandas as pd
from plot_style import *

prot = pd.read_csv(O / 'figure3_protocols.csv')
rep = pd.read_csv(O / 'figure3_repeats.csv')

TARGETS = ['Curie(TC) (K)', 'Coercivity (Oe)']
TLAB = {'Curie(TC) (K)': r'$T_C$', 'Coercivity (Oe)': r'$\log_{10} H_c$'}

fig, axs = plt.subplots(2, 2, figsize=(9.0, 6.9), layout='constrained')

# (a) protocol comparison ----------------------------------------------------
ax = axs[0, 0]
order = ['notebook_random', 'composition_random', 'grouped_single_v2', 'grouped_repeated_v3']
names = ['Notebook\nrandom', 'Composition\nrandom', 'Grouped\nsingle split', 'Grouped\n20 repeats']
w = 0.38
for k, t in enumerate(TARGETS):
    g = prot[prot.target == t].set_index('protocol').loc[order]
    x = np.arange(len(order)) + (k - 0.5) * w
    ax.bar(x, g.r2, width=w, color=COLORS[k], label=TLAB[t],
           yerr=np.where(g.r2_sd.isna(), 0, g.r2_sd), capsize=3,
           error_kw=dict(lw=1.0, ecolor='#444444'))
    for xi, v, s in zip(x, g.r2, g.r2_sd):
        ax.text(xi, v + (0.02 if np.isnan(s) else s + 0.02), f'{v:.2f}',
                ha='center', fontsize=8.2)
ax.set(xticks=np.arange(len(order)), xticklabels=names, ylabel=r'Test $R^2$', ylim=(0, 0.95))
ax.tick_params(axis='x', labelsize=8.2)
ax.legend(frameon=False, fontsize=8.6, loc='upper right')
ax.axvspan(-0.5, 1.5, color='#D55E00', alpha=0.06)
ax.text(0.5, 0.90, 'shared compositions\nacross the split', ha='center', fontsize=8.0,
        color='#9A4500')

# (b) spread across the twenty repeats ---------------------------------------
ax = axs[0, 1]
for k, t in enumerate(TARGETS):
    g = rep[(rep.target == t) & (rep.split != 'v2_reference_split')]
    jitter = (np.random.RandomState(3).rand(len(g)) - 0.5) * 0.22
    ax.scatter(np.full(len(g), k) + jitter, g.r2, s=26, color=COLORS[k],
               alpha=0.75, edgecolors='none')
    ax.hlines(g.r2.mean(), k - 0.28, k + 0.28, color='#333333', lw=1.6)
    ax.hlines([g.r2.mean() - g.r2.std(), g.r2.mean() + g.r2.std()],
              k - 0.18, k + 0.18, color='#333333', lw=0.9, linestyles='--')
    v2 = rep[(rep.target == t) & (rep.split == 'v2_reference_split')].r2.iloc[0]
    ax.scatter([k], [v2], marker='*', s=190, color='#D55E00', zorder=5,
               edgecolors='white', linewidths=0.6)
    ax.annotate('single split\nused in v2', xy=(k + 0.06, v2),
                xytext=(k + 0.30, v2 + (0.085 if k == 0 else 0.075)),
                fontsize=7.4, color='#9A4500', va='center', linespacing=1.3,
                arrowprops=dict(arrowstyle='-', color='#9A4500', lw=0.7))
ax.set(xticks=[0, 1], xticklabels=[TLAB[t] for t in TARGETS],
       ylabel=r'Test $R^2$ per repeat', xlim=(-0.5, 1.95), ylim=(0.25, 0.83))
ax.text(0.98, 0.04, 'mean (solid) and $\\pm$1 s.d. (dashed)', transform=ax.transAxes,
        fontsize=7.8, color='#444444', ha='right')

# (c) why one split is not enough -------------------------------------------
ax = axs[1, 0]
g = rep[rep.target == 'Curie(TC) (K)']
sd = np.linspace(230, 330, 100)
for r2v, ls in [(0.33, ':'), (0.5, '-.'), (0.6, '--'), (0.7, '-')]:
    ax.plot(sd, sd * np.sqrt(1 - r2v), color='#AAAAAA', ls=ls, lw=0.9,
            clip_on=True)
    yl = 331 * np.sqrt(1 - r2v)
    if 132 < yl < 233:
        ax.text(332, yl, f'$R^2$={r2v:g}', fontsize=7.4, color='#888888', va='center')
    else:
        xl = 204 / np.sqrt(1 - r2v)
        ax.text(xl - 1, 207, f'$R^2$={r2v:g}', fontsize=7.4, color='#888888',
                ha='right', rotation=34)
m = g.split == 'v2_reference_split'
ax.scatter(g.loc[~m, 'test_target_sd'], g.loc[~m, 'rmse'], s=34, color=COLORS[0],
           alpha=0.85, edgecolors='none', label='20 repeats')
ax.scatter(g.loc[m, 'test_target_sd'], g.loc[m, 'rmse'], marker='*', s=230,
           color='#D55E00', zorder=5, edgecolors='white', linewidths=0.6,
           label='single split used in v2')
ax.set(xlabel=r'Standard deviation of $T_C$ in the held-out split (K)',
       ylabel='Held-out RMSE (K)', xlim=(232, 345), ylim=(130, 235))
ax.legend(frameon=False, fontsize=8.0, loc='upper left')
ax.text(0.03, 0.06,
        'the v2 split has a typical error but the\nnarrowest held-out spread, so its $R^2$ is lowest',
        transform=ax.transAxes, fontsize=7.8, color='#444444', linespacing=1.35)

# (d) composition overlap ----------------------------------------------------
ax = axs[1, 1]
ov = prot.drop_duplicates('protocol').set_index('protocol').loc[order]
bars = ax.bar(np.arange(len(order)), ov.test_rows_sharing_a_training_composition,
              color=['#D55E00', '#D55E00', COLORS[0], COLORS[0]], width=0.6)
for i, v in enumerate(ov.test_rows_sharing_a_training_composition):
    ax.text(i, v + 4, str(int(v)), ha='center', fontsize=9)
ax.set(xticks=np.arange(len(order)), xticklabels=names,
       ylabel='Test records whose composition\nalso appears in training', ylim=(0, 205))
ax.tick_params(axis='x', labelsize=8.2)

for ax, l in zip(axs.flat, 'abcd'):
    panel(ax, l)
save(fig, 3)
print('figure3 written')
