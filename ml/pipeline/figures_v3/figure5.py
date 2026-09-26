"""Figure 5. Which descriptors the held-out-composition models actually use.

SHAP values are computed with a tree explainer on the composition-grouped test
partition of the reference split, so the attributions describe behaviour on
compositions the model never saw.

Inputs : figure5_shap_tc.csv, figure5_shap_hc.csv, figure5_importance.csv
Outputs: figure5.png (600 dpi), figure5.pdf, figure5.svg
"""
import numpy as np
import pandas as pd
from plot_style import *

tc = pd.read_csv(O / 'figure5_shap_tc.csv')
hc = pd.read_csv(O / 'figure5_shap_hc.csv')
imp = pd.read_csv(O / 'figure5_importance.csv')

PRETTY = {
    'x_Fe': 'Fe fraction', 'x_Co': 'Co fraction', 'x_Ni': 'Ni fraction',
    'x_Mn': 'Mn fraction', 'x_O': 'O fraction', 'x_B': 'B fraction',
    'x_Si': 'Si fraction', 'x_Al': 'Al fraction', 'x_Cu': 'Cu fraction',
    'x_Nd': 'Nd fraction', 'x_Sm': 'Sm fraction', 'x_Gd': 'Gd fraction',
    'x_Cr': 'Cr fraction', 'x_Zr': 'Zr fraction', 'x_Nb': 'Nb fraction',
    'VEC': 'VEC', 'rho_theoretical (g/cm^3)': 'arithmetic density',
    'f_ferromagnetic_host': 'Fe+Co+Ni fraction', 'f_3d': '3d fraction',
    'f_rare_earth': 'rare-earth fraction', 'f_metalloid': 'metalloid fraction',
    'f_chalcogen_halogen': 'O/S/Se/halogen fraction', 'f_light_metal': 'light-metal fraction',
    'mixing_entropy': 'ideal mixing entropy', 'n_components': 'number of components',
    'size_mismatch_delta': 'size mismatch $\\delta$', 'x_max': 'largest fraction',
    'electronegativity_mismatch': 'electronegativity mismatch',
}


def label(c):
    if c in PRETTY:
        return PRETTY[c]
    if c.startswith('x_'):
        return c[2:] + ' fraction'
    c = (c.replace('gs_magmom', 'elemental moment')
          .replace('melting_point', 'melting point')
          .replace('boiling_point', 'boiling point')
          .replace('heat_of_formation', 'atomisation enthalpy')
          .replace('electronegativity', 'electronegativity')
          .replace('thermal_conductivity', 'thermal conductivity')
          .replace('ionization_energy', 'ionisation energy')
          .replace('molar_volume', 'molar volume')
          .replace('covalent_radius', 'covalent radius')
          .replace('mendeleev_number', 'Mendeleev number')
          .replace('nvalence', 'valence electrons')
          .replace('n_d', '$n_d$').replace('n_f', '$n_f$')
          .replace('n_s', '$n_s$').replace('n_p', '$n_p$'))
    for a, b in [('_mean', ' (mean)'), ('_absdev', ' (spread)'), ('_max', ' (max)'),
                 ('_min', ' (min)'), ('_range', ' (range)'), ('_mode', ' (mode)')]:
        c = c.replace(a, b)
    return c.replace('_', ' ')


def beeswarm(ax, d, cmap, title):
    feats = (d.groupby('feature').shap.apply(lambda s: s.abs().mean())
              .sort_values(ascending=True).tail(10).index.tolist())
    rng = np.random.RandomState(0)
    for i, f in enumerate(feats):
        g = d[d.feature == f]
        v = g.value.to_numpy()
        rank = (np.argsort(np.argsort(v)) / max(len(v) - 1, 1)) if len(v) > 1 else np.zeros(len(v))
        y = i + (rng.rand(len(g)) - 0.5) * 0.34
        ax.scatter(g.shap, y, c=rank, cmap=cmap, s=7, alpha=0.7,
                   edgecolors='none', rasterized=True, vmin=0, vmax=1)
    ax.axvline(0, color='#888888', lw=0.7)
    ax.set_yticks(range(len(feats)))
    ax.set_yticklabels([label(f) for f in feats], fontsize=8.0)
    ax.set_title(title, fontsize=10)
    return feats


fig, axs = plt.subplots(2, 2, figsize=(9.4, 7.2), layout='constrained')

f_tc = beeswarm(axs[0, 0], tc, 'viridis', r'Curie temperature')
axs[0, 0].set_xlabel('SHAP value (K)')
f_hc = beeswarm(axs[0, 1], hc, 'plasma', r'Logarithmic coercivity')
axs[0, 1].set_xlabel(r'SHAP value ($\log_{10}$ units)')
sm = plt.cm.ScalarMappable(cmap='viridis', norm=plt.Normalize(0, 1))
fig.colorbar(sm, ax=axs[0, :], shrink=0.7, ticks=[0, 1], pad=0.015
             ).set_ticklabels(['low', 'high'])

# (c,d) permutation importance on held-out compositions ----------------------
for k, (t, col, ax) in enumerate([('Curie(TC) (K)', COLORS[0], axs[1, 0]),
                                  ('Coercivity (Oe)', COLORS[1], axs[1, 1])]):
    g = imp[imp.target == t].sort_values('importance_mean').tail(10)
    ax.barh(np.arange(len(g)), g.importance_mean, xerr=g.importance_sd,
            color=col, height=0.66, error_kw=dict(lw=0.9, ecolor='#444444'))
    ax.set_yticks(np.arange(len(g)))
    ax.set_yticklabels([label(f) for f in g.feature], fontsize=8.0)
    ax.set_xlabel(r'Permutation importance (drop in $R^2$)')
    ax.set_title('Curie temperature' if k == 0 else 'Logarithmic coercivity', fontsize=10)

for ax, l in zip(axs.flat, 'abcd'):
    panel(ax, l)
save(fig, 5)
print('figure5 written')
