"""Import a mesh, select one smooth face group, and map a lattice onto it.

The domed tile is a closed solid with three distinct face groups -- a domed top, four vertical
sides, and a flat bottom. Angle-limited linked selection isolates the top as a single clean disk,
which is converted to ``TriangleMeshSurface``. The free-boundary parameterization
keeps the patch's real outline and trims the mapped lattice to it, and the wall thickness is
graded across the patch, so this is the general recipe for driving a graded conformal lattice
from an imported mesh region without manually reconstructing indexed arrays.
"""

from pathlib import Path

import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz

# Import the closed solid and choose the domed top from a geometric seed point.
tile_path = Path(__file__).resolve().parents[2] / "data" / "3d_models" / "domed_tile.stl"
tile = pv.SurfaceMesh(str(tile_path), disable_validation=True)
seed = tile.nearest_triangle(pv.Vec3(0, 0, 100))
top = tile.select_linked_by_face_angle(seed.triangle_id, max_angle_degrees=30.0)

# Turn the extracted top into the open surface that will guide the lattice.
surface = top.to_triangle_mesh_surface(u_axis_hint=pv.Vec3(1, 0, 0))
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
