"""Map a gyroid onto a domed mesh patch with vents, and seal the vents with a rim.

The patch has five round openings. ``TriangleMeshSurface`` treats each opening as a trim: it
fills the hole internally so the patch flattens smoothly, then reports the hole as off the
surface. The cell map's default ``trim="boundary"`` therefore keeps the lattice out of every
vent, and ``mm.rim`` seals the vent walls as well as the outer edge.
"""

import math
import sys
from pathlib import Path

import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _triangle_surface_examples import indexed_holed_grid

BLOCK = 12.0          # mm, one block of the 5 x 5 patch
DOME_RADIUS = 70.0    # mm, radius of the spherical cap the patch follows
VENTS = {(1, 1): 3.5, (3, 1): 4.0, (2, 2): 4.5, (1, 3): 4.0, (3, 3): 3.5}


def dome(x, y):
    return math.sqrt(DOME_RADIUS * DOME_RADIUS - x * x - y * y) - DOME_RADIUS


# Build the vented patch: the vents become interior boundary loops of the mesh.
vertices, triangles = indexed_holed_grid(BLOCK, 5, 5, VENTS, 6, 4, dome)
surface = pv.TriangleMeshSurface(vertices, triangles)
print(f"{surface.hole_count} vents filled internally with {surface.filled_triangle_count} triangles")

# One layer of 6 mm cells, 5 mm tall. Trimming removes the lattice from every vent.
cell_map = mm.cell_map_from_surface(surface, cells=(10, 10, 1), height=5.0)

# Seal the cut cells along the outer edge and around each vent.
root = pv.Union(
    mm.gyroid(cell_map, wall_thickness=0.6),
    mm.rim(cell_map, width=1.2),
)

viz.Render(root)
