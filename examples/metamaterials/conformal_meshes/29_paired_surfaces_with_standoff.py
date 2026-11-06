"""Fill the space between two saddle patches, standing the lattice off the lower one.

``mm.cell_map_between_surfaces`` interpolates between two surfaces. ``standoff`` first moves
the lower (first) surface along its normal, so the lattice keeps a clearance from it while
still ending on the upper surface.
"""

import sys
from pathlib import Path

import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _triangle_surface_examples import grid_surface

STANDOFF = 2.0   # mm clearance above the lower surface


def lower_saddle(x, y):
    return 0.012 * (x * x - y * y)


def upper_saddle(x, y):
    return 10.0 + 0.008 * (x * x - y * y)


lower = grid_surface(40.0, 40.0, 21, 21, lower_saddle)
upper = grid_surface(40.0, 40.0, 21, 21, upper_saddle)

cell_map = mm.cell_map_between_surfaces(lower, upper, cells=(6, 6, 2), standoff=STANDOFF)
root = mm.octet(cell_map, beam_radius=0.6)

viz.Render(root)
