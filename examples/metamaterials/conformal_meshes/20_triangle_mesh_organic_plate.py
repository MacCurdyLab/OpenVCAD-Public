"""Map a plate lattice onto an elongated undulating triangle-mesh patch.

The patch is a 60 x 20 mm strip, so its chart is a matching elongated rectangle: the
parameterization preserves the patch's aspect ratio instead of squashing it onto a square, and
lattice cells stay near-uniform along both directions. The ``u_axis_hint`` pins the chart's U
axis to the strip's long world direction; the default principal-axis alignment would pick the
same orientation here, but the hint makes the beam orientation explicit.
"""

import math

import sys
from pathlib import Path

import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _triangle_surface_examples import indexed_grid


def undulating(x, y):
    wave = 2.0 * math.sin(math.pi * x / 15.0) * math.cos(math.pi * y / 12.0)
    bump = 3.0 * math.exp(-((x - 12.0) ** 2 + (y + 4.0) ** 2) / 40.0)
    return wave + bump


# Make a long, wavy mesh strip. It is three times longer than it is wide.
vertices, triangles = indexed_grid(60.0, 20.0, 25, 9, undulating)
# Keep the lattice U direction along world X, the strip's long direction.
surface = pv.TriangleMeshSurface(vertices, triangles, u_axis_hint=pv.Vec3(1.0, 0.0, 0.0))
# Use a matching 15 x 5 cell grid, then build plates through its 4.5 mm height.
cell_map = mm.cell_map_from_surface(
    surface,
    cells=(15, 5, 1),
    height=4.5,
    linear=False,
)
# Fill the mapped cells with triangular plates rather than beams.
root = mm.plate_lattice(
    cell_map,
    wall_thickness=0.4,
    eccentricity=1.0,
    surface_mode="triangulated",
)

viz.Render(root)
