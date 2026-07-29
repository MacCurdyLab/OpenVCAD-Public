"""Map an FCC beam lattice onto a saddle-shaped triangle-mesh patch.

The goal is to show that a lattice can follow a surface that curves up in one direction and down
in the other. The mesh resolution describes the saddle; the cell counts independently control the
number of FCC lattice cells placed across it.
"""

import sys
from pathlib import Path

import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _triangle_surface_examples import grid_surface


def saddle(x, y):
    return 0.02 * (x * x - y * y)


# Build the saddle mesh first. Its 14 x 14 vertices describe the source surface, not the lattice.
surface = grid_surface(30.0, 30.0, 14, 14, saddle)
# Put a 12 x 10 layer of cells over the saddle and extend it 5 mm along its surface normals.
cell_map = mm.cell_map_from_surface(
    surface,
    cells=(12, 10, 1),
    height=5.0,
    linear=False,
)
# Use FCC beams so their directions make the curved mapping easy to see.
root = mm.fcc(cell_map, beam_radius=0.3)

viz.Render(root)
