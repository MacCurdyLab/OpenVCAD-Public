"""Import a mesh, extract one face group, and map a lattice onto it.

The domed tile is a closed solid with three distinct face groups -- a domed top, four vertical
sides, and a flat bottom. Selecting the upward-facing triangles isolates the top as a single clean
disk, which is supplied directly to ``TriangleMeshSurface``. The free-boundary parameterization
keeps the patch's real outline and trims the mapped lattice to it, and the wall thickness is
graded across the patch, so this is the general recipe for driving a graded conformal lattice
from an imported mesh region using only ``SurfaceMesh``'s indexed arrays.
"""

import sys
from pathlib import Path

import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _triangle_surface_examples import (
    largest_connected_component,
    reindex,
    select_triangles,
)

# Import the closed solid and work directly with its indexed vertices and triangles.
tile_path = Path(__file__).resolve().parents[2] / "data" / "3d_models" / "domed_tile.stl"
tile = pv.SurfaceMesh(str(tile_path), disable_validation=True)
vertices = tile.vertices
triangles = tile.triangles

# Extract the upward-facing top face group, keep its largest connected patch, and reindex it into a
# standalone disk mesh.
top = select_triangles(vertices, triangles, lambda nx, ny, nz: nz > 0.5)
top = largest_connected_component(top)
patch_vertices, patch_triangles = reindex(vertices, top)

# Turn the extracted top into the open surface that will guide the lattice.
surface = pv.TriangleMeshSurface(patch_vertices, patch_triangles)
# Build a single cell layer that follows the domed top.
cell_map = mm.cell_map_from_surface(
    surface,
    cells=(12, 12, 1),
    height=3.0,
    linear=False,
)


# Make the gyroid wall thicker from one side of the patch to the other.
graded_wall = cell_map.logical_position.x.map_range(0.0, 12.0, 0.45, 0.90)
root = mm.gyroid(cell_map, wall_thickness=graded_wall)

viz.Render(root)
