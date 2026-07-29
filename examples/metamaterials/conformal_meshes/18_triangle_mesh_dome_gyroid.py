"""Map a conformal gyroid onto a circular domed triangle-mesh patch.

The patch is a spherical-cap dome over a round boundary -- a shape the free-boundary conformal
parameterization handles naturally. The chart keeps the patch's circular outline inside its UV
bounding rectangle, and the map's trim mode decides what happens in the empty rectangle corners.
Edit ``TRIM_MODE`` to compare the three options:

- ``pv.TrimMode.boundary`` (default): the gyroid is clipped smoothly at the dome's true round
  edge.
- ``pv.TrimMode.cells``: whole boundary cells are kept or dropped, so the edge is blocky.
- ``pv.TrimMode.none``: the full rectangular cell grid is kept and the corners extrapolate past
  the round edge.
"""

import math

import sys
from pathlib import Path

import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _triangle_surface_examples import disk_surface

RADIUS = 15.0
DOME_HEIGHT = 8.0
TRIM_MODE = pv.TrimMode.boundary


def spherical_cap(x, y):
    r2 = (x * x + y * y) / (RADIUS * RADIUS)
    return DOME_HEIGHT * math.sqrt(max(0.0, 1.0 - 0.75 * r2))


# Build the round dome patch that the gyroid will follow.
surface = disk_surface(RADIUS, 10, 36, spherical_cap)
# Create one layer of cells above the dome; TRIM_MODE controls how its circular edge ends.
cell_map = mm.cell_map_from_surface(
    surface,
    cells=(12, 12, 1),
    height=4.0,
    linear=False,
    trim=TRIM_MODE,
)
# Fill the mapped cells with a constant-thickness gyroid sheet.
root = mm.gyroid(cell_map, wall_thickness=0.7)

viz.Render(root)
