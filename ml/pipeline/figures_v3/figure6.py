"""Figure 6. The recipe generator: what survives once the calibrated prediction
interval and the distance to known chemistry are both enforced, and which
threshold pairs the generator can actually resolve.

Inputs : figure6_candidates.csv, figure6_top.csv, figure6_distance.csv,
         figure6_resolution.csv  (figure6_funnel.csv is quoted in the text)
Outputs: figure6.png (600 dpi), figure6.pdf, figure6.svg
"""
import numpy as np
import pandas as pd
from plot_style import *

cand = pd.read_csv(O / 'figure6_candidates.csv')
top = pd.read_csv(O / 'figure6_top.csv')
dist = pd.read_csv(O / 'figure6_distance.csv')
res = pd.read_csv(O / 'figure6_resolution.csv')

TC_T, HC_T = 1000.0, 100.0
NOV = {'interpolation': COLORS[2], 'near-extrapolation': COLORS[4],
       'far-extrapolation': '#BBBBBB'}

fig, axs = plt.subplots(2, 2, figsize=(9.6, 7.4), layout='constrained')

# (a) the design plane -------------------------------------------------------
ax = axs[0, 0]
for name in ['far-extrapolation', 'near-extrapolation', 'interpolation']:
    g = cand[cand.novelty == name]
    ax.scatter(g.predicted_Hc_Oe, g.predicted_Tc_K, s=5, color=NOV[name],
               alpha=0.45, edgecolors='none', rasterized=True, label=name)
s = cand[cand.point_pass]
ax.scatter(s.predicted_Hc_Oe, s.predicted_Tc_K, s=30, facecolors='none',
           edgecolors='#C1272D', linewidths=0.9, zorder=5,
           label=f'{len(s)} point-prediction hits')
ax.set_xscale('log')
ax.axhline(TC_T, color='#555555', ls='--', lw=1)
ax.axvline(HC_T, color='#555555', ls='--', lw=1)
ax.set(xlabel=r'Predicted $H_c$ (Oe)', ylabel=r'Predicted $T_C$ (K)')
ax.legend(frameon=False, fontsize=7.4, loc='lower left', markerscale=1.7,
          handletextpad=0.5)
ax.text(0.97, 0.955, 'target quadrant', ha='right', va='top',
        transform=ax.transAxes, fontsize=8.2, color='#555555')

# (b) ranked recipes with their intervals ------------------------------------
ax = axs[0, 1]
t = top.head(10).iloc[::-1].reset_index(drop=True)
y = np.arange(len(t))
ax.errorbar(t.predicted_Tc_K, y, xerr=[t.predicted_Tc_K - t.Tc_lower_K,
                                       t.Tc_upper_K - t.predicted_Tc_K],
            fmt='o', color=COLORS[0], ms=5, lw=1.1, capsize=3)
ax.axvline(TC_T, color='#555555', ls='--', lw=1)
ax.set_yticks(y)
ax.set_yticklabels([f"Fe{100*r.Fe:.0f}Co{100*r.Co:.0f}Ni{100*r.Ni:.0f}"
                    f"Mn{100*r.Mn:.0f}Al{100*r.Al:.0f}Si{100*r.Si:.0f}"
                    for _, r in t.iterrows()], fontsize=7.0)
ax.set_xlabel(r'Predicted $T_C$ with 90% conformal interval (K)')
ax.set_title('Ten highest-ranked candidates', fontsize=10)
ax.set_ylim(-1.15, len(t) - 0.35)
ax.text(0.5, 0.015, 'every interval crosses the 1000 K threshold',
        transform=ax.transAxes, fontsize=7.6, color='#8E1B20', ha='center')

# (c) novelty gate -----------------------------------------------------------
ax = axs[1, 0]
hi = float(np.quantile(dist.distance, 0.99))
bins = np.linspace(0, max(hi, 0.9), 46)
for name, col, lab in [('calibration', COLORS[2], 'held-out compositions\n(where coverage was measured)'),
                       ('candidate', COLORS[3], 'generated candidates')]:
    g = dist[dist.kind == name]
    ax.hist(g.distance, bins=bins, density=True, color=col, alpha=0.55,
            edgecolor='white', linewidth=0.3, label=lab)
top_y = ax.get_ylim()[1]
for q, ls, lab in [(dist.d50.iloc[0], '--', 'median'), (dist.d90.iloc[0], ':', '90th pct')]:
    ax.axvline(q, color='#444444', ls=ls, lw=1.1)
    ax.text(q + 0.012, top_y * 0.52, lab, fontsize=7.4, rotation=90, va='top',
            color='#444444')
ax.set(xlabel=r'$L_1$ distance to the nearest fitting composition', ylabel='Density')
ax.legend(frameon=False, fontsize=7.4, loc='upper right')

# (d) what the generator can resolve ----------------------------------------
ax = axs[1, 1]
piv = res.pivot(index='tc_threshold', columns='hc_threshold', values='n_interval_robust')
Xg, Yg = np.meshgrid(piv.columns.to_numpy(), piv.index.to_numpy())
Z = piv.to_numpy().astype(float)
pc = ax.pcolormesh(Xg, Yg, np.log10(Z + 1), cmap='YlGnBu', shading='nearest')
cs = ax.contour(Xg, Yg, Z, levels=[1, 10, 100, 1000], colors='#333333', linewidths=0.8)
ax.clabel(cs, fmt=lambda v: f'{int(v)}', fontsize=7.0, inline_spacing=3)
ax.set_xlim(1, 8e3)
ax.set_xscale('log')
ax.scatter([HC_T], [TC_T], marker='X', s=130, color='#C1272D', zorder=6,
           edgecolors='white', linewidths=0.8)
ax.annotate('target used in the\noriginal draft:\nno supported recipe',
            xy=(HC_T, TC_T), xytext=(2.6, 900), fontsize=7.2, color='#8E1B20',
            linespacing=1.3,
            arrowprops=dict(arrowstyle='->', color='#8E1B20', lw=0.8))
cb = fig.colorbar(pc, ax=ax, shrink=0.88, pad=0.02)
cb.set_label(r'Supported recipes, $\log_{10}(n+1)$', fontsize=8.2)
cb.ax.tick_params(labelsize=7.6)
ax.set(xlabel='Coercivity threshold (Oe)', ylabel='Curie-temperature threshold (K)')
ax.set_title('Resolvable design envelope', fontsize=10)

for ax, l in zip(axs.flat, 'abcd'):
    panel(ax, l)
save(fig, 6)
print('figure6 written')
