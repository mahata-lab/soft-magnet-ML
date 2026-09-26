"""Render the eight figures from saved CSV tables; no fitting or simulation."""
from pathlib import Path
import runpy
for n in range(1,9):
 print(f'Rendering figure {n}',flush=True)
 runpy.run_path(str(Path(__file__).parent/f'figure{n}.py'))
