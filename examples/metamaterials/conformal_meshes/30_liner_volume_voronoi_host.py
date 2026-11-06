"""Use a conformal map's volume as the host for a random Voronoi lattice.

``mm.domain(cell_map)`` turns the trimmed map volume into a solid node: negative inside the
mapped shell and positive outside, in the trimmed margins, and in the vents. Here it hosts a
stochastic Voronoi strut lattice that follows the curved, vented dome, and a rim seals the
edges.
"""

import math
import sys
from pathlib import Path

import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _triangle_surface_examples import indexed_holed_grid

DOME_RADIUS = 70.0
VENTS = {(1, 1): 4.0, (3, 1): 4.0, (2, 3): 4.5}


def dome(x, y):
    return math.sqrt(DOME_RADIUS * DOME_RADIUS - x * x - y * y) - DOME_RADIUS


vertices, triangles = indexed_holed_grid(12.0, 5, 5, VENTS, 6, 4, dome)
surface = pv.TriangleMeshSurface(vertices, triangles)
cell_map = mm.cell_map_from_surface(surface, cells=(10, 10, 1), height=8.0)

# The mapped shell as a solid host, prepared before seeds are sampled inside it.
host = mm.domain(cell_map)
host.prepare(pv.Vec3(0.5, 0.5, 0.5), 1.0)
seeds = mm.sample_points_in_host(host, spacing=5.0, seed=7, boundary_clearance=0.5)
print(f"{len(seeds)} Voronoi seeds inside the liner volume")

root = pv.Union(
    mm.voronoi_graph_lattice(host, seeds, beam_thickness=0.9),
    mm.rim(cell_map, width=1.2),
)

viz.Render(root)
