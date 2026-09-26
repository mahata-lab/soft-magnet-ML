"""Figure 1. Workflow schematic: the leakage-controlled statistical branch that
produces the recipe generator, and the separate first-principles and atomistic
branch that bounds how far the recipes may be interpreted physically.

Input : figure1.csv  (stage table; text and grid positions only)
Output: figure1.png (600 dpi), figure1.pdf, figure1.svg
"""
import textwrap

import pandas as pd
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from plot_style import *

d = pd.read_csv(O / 'figure1.csv')

STYLE = {'data':      dict(fill='#EBF2FA', edge='#1965B0', title='#14477E'),
         'benchmark': dict(fill='#F5F1E8', edge='#8A7446', title='#6B5A33'),
         'output':    dict(fill='#E7F4EF', edge='#009E73', title='#0B6B50')}

COL_X = [0.0, 4.15, 8.30, 12.45]
ROW_Y = {0: 3.55, 1: 0.10}
W, H = 3.70, 2.46

fig, ax = plt.subplots(figsize=(12.2, 5.9))
ax.set(xlim=(-0.25, 16.5), ylim=(-0.55, 6.85))
ax.axis('off')

centres = {}
for _, r in d.iterrows():
    s = STYLE[r.kind]
    x, y = COL_X[r.col], ROW_Y[r.row]
    centres[r.stage] = (x, y)
    ax.add_patch(FancyBboxPatch((x, y), W, H,
                                boxstyle='round,pad=0.05,rounding_size=0.08',
                                facecolor=s['fill'], edgecolor=s['edge'], linewidth=1.2))
    ax.text(x + 0.16, y + H - 0.30, r.stage, weight='bold', fontsize=9.9, color=s['title'])
    body = '\n'.join(textwrap.fill(line, 31) for line in r.detail.split('|'))
    ax.text(x + 0.16, y + H - 0.60, body, fontsize=8.7, va='top',
            color='#1F1F1F', linespacing=1.42)
    note = '\n'.join(textwrap.fill(line, 37) for line in r.note.split('|'))
    ax.text(x + 0.16, y + 0.14, note, fontsize=7.5, va='bottom', style='italic',
            color='#5E5E5E', linespacing=1.36)


def arrow(p0, p1, color='#3A3A3A', rad=0.0, lw=1.2):
    ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle='-|>', mutation_scale=12,
                                 color=color, linewidth=lw, shrinkA=0, shrinkB=0,
                                 connectionstyle=f'arc3,rad={rad}'))


for c in range(3):
    arrow((COL_X[c] + W, ROW_Y[0] + H / 2), (COL_X[c + 1] - 0.05, ROW_Y[0] + H / 2))
for c in range(2):
    arrow((COL_X[c] + W, ROW_Y[1] + H / 2), (COL_X[c + 1] - 0.05, ROW_Y[1] + H / 2),
          color='#8A7446')

# Calibrated models feed the generator; benchmarks constrain its interpretation.
arrow((COL_X[3] + W / 2, ROW_Y[0] - 0.03), (COL_X[3] + W / 2, ROW_Y[1] + H + 0.05))
ax.add_patch(FancyArrowPatch((COL_X[2] + W, ROW_Y[1] + H / 2),
                             (COL_X[3] - 0.05, ROW_Y[1] + H / 2),
                             arrowstyle='-|>', mutation_scale=12, color='#8A7446',
                             linewidth=1.2, linestyle=(0, (3, 2)), shrinkA=0, shrinkB=0))

ax.text(COL_X[3] + W / 2 + 0.16, ROW_Y[1] + H + 0.30,
        'calibrated models', fontsize=8.4, color='#14477E', va='bottom')

ax.text(-0.2, 6.45, 'Statistical branch  —  compiled literature data',
        fontsize=10.6, weight='bold', color='#14477E')
ax.text(-0.2, 2.98, 'Physical branch  —  existing first-principles and atomistic outputs',
        fontsize=10.6, weight='bold', color='#6B5A33')
ax.plot([-0.2, 16.3], [6.28, 6.28], color='#1965B0', lw=0.8, alpha=0.35)
ax.plot([-0.2, 16.3], [2.81, 2.81], color='#8A7446', lw=0.8, alpha=0.35)

save(fig, 1)
print('figure1 written')
