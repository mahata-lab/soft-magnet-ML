"""Figure 4. Descriptor sets, held-out parity and the calibration of the
prediction intervals used by the recipe generator.

Inputs : figure4_parity.csv, figure4_descriptors.csv, figure4_coverage.csv
Outputs: figure4.png (600 dpi), figure4.pdf, figure4.svg
"""
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, r2_score
from plot_style import *

par = pd.read_csv(O / 'figure4_parity.csv')
des = pd.read_csv(O / 'figure4_descriptors.csv')
cov = pd.read_csv(O / 'figure4_coverage.csv')

TARGETS = ['Curie(TC) (K)', 'Coercivity (Oe)']
UNIT = {'Curie(TC) (K)': r'$T_C$ (K)',
        'Coercivity (Oe)': r'$\log_{10}[H_c/(1\ \mathrm{Oe})]$'}
TLAB = {'Curie(TC) (K)': r'$T_C$', 'Coercivity (Oe)': r'$\log_{10} H_c$'}

fig, axs = plt.subplots(2, 2, figsize=(9.4, 7.4), layout='constrained')

# (a,b) parity on held-out compositions --------------------------------------
for k, t in enumerate(TARGETS):
    ax = axs[0, k]
    g = par[par.target == t]
    q = g.conformal_halfwidth.mean()
    lo = min(g.observed.min(), g.predicted.min())
    hi = max(g.observed.max(), g.predicted.max())
    pad = 0.04 * (hi - lo)
    xs = np.array([lo - pad, hi + pad])
    ax.fill_between(xs, xs - q, xs + q, color=COLORS[k], alpha=0.16, lw=0,
                    label='90% conformal band (mean width)')
    ax.scatter(g.observed, g.predicted, s=5, color=COLORS[k], alpha=0.28,
               edgecolors='none', rasterized=True)
    ax.plot(xs, xs, color='#555555', ls='--', lw=1)
    fmt = '.1f' if k == 0 else '.3f'
    ax.text(0.04, 0.955,
            f'pooled over 20 grouped repeats\n$n$ = {len(g):,} held-out records\n'
            f'$R^2$ = {r2_score(g.observed, g.predicted):.3f}\n'
            f'MAE = {mean_absolute_error(g.observed, g.predicted):{fmt}}',
            va='top', transform=ax.transAxes, fontsize=8.5, linespacing=1.4)
    ax.set(xlabel='Observed ' + UNIT[t], ylabel='Predicted ' + UNIT[t],
           xlim=xs, ylim=xs)
    ax.legend(loc='lower right', frameon=False, fontsize=8.2)

# (c) descriptor-set comparison ----------------------------------------------
ax = axs[1, 0]
sets = ['fractions', 'physics', 'combined']
labels = ['Elemental\nfractions', 'Weighted elemental\nstatistics', 'Both']
w = 0.38
for k, t in enumerate(TARGETS):
    g = des[des.target == t].set_index('feature_set').loc[sets]
    x = np.arange(3) + (k - 0.5) * w
    ax.bar(x, g.r2_mean, width=w, color=COLORS[k], label=TLAB[t],
           yerr=g.r2_sd, capsize=3, error_kw=dict(lw=1.0, ecolor='#444444'))
    for xi, v, s in zip(x, g.r2_mean, g.r2_sd):
        ax.text(xi, v + s + 0.015, f'{v:.3f}', ha='center', fontsize=7.8)
ax.set(xticks=np.arange(3), xticklabels=labels, ylabel=r'Grouped $R^2$ (20 repeats)',
       ylim=(0, 0.85))
ax.tick_params(axis='x', labelsize=8.2)
ax.legend(frameon=False, fontsize=8.6, ncol=2, loc='upper left')

# (d) interval calibration ---------------------------------------------------
ax = axs[1, 1]
ax.plot([0.5, 1.0], [0.5, 1.0], color='#555555', ls='--', lw=1, label='ideal')
for k, t in enumerate(TARGETS):
    g = cov[cov.target == t].sort_values('nominal')
    ax.plot(g.nominal, g.empirical, 'o-', color=COLORS[k], lw=1.5, ms=5,
            label=TLAB[t])
ax.set(xlabel='Nominal conformal level', ylabel='Empirical coverage,\nheld-out compositions',
       xlim=(0.49, 1.03), ylim=(0.46, 1.03))
ax.legend(frameon=False, fontsize=8.6, loc='upper left')
tc2 = cov[cov.target == 'Curie(TC) (K)'].tree_coverage_at_2sd.iloc[0]
hc2 = cov[cov.target == 'Coercivity (Oe)'].tree_coverage_at_2sd.iloc[0]
ax.scatter([0.95, 0.95], [tc2, hc2], marker='X', s=95, color='#C1272D', zorder=6,
           edgecolors='white', linewidths=0.6)
ax.annotate('tree spread $\\pm2$ s.d.\nread as a 95% interval',
            xy=(0.95, min(tc2, hc2)), xytext=(0.70, 0.52), fontsize=7.6,
            color='#8E1B20', linespacing=1.3,
            arrowprops=dict(arrowstyle='->', color='#8E1B20', lw=0.8))

for ax, l in zip(axs.flat, 'abcd'):
    panel(ax, l)
save(fig, 4)
print('figure4 written')
