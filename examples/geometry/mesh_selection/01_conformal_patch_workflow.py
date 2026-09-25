"""Select a smooth region from a closed mesh and conformally map a lattice onto it."""

from pathlib import Path

import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz


tile_path = Path(__file__).resolve().parents[2] / "data" / "3d_models" / "domed_tile.stl"
mesh = pv.SurfaceMesh(str(tile_path), disable_validation=True)

# A point above the part finds a seed triangle without relying on a fragile triangle ID. Local
# face-angle growth follows the smooth dome and stops at the sharp edge where the side wall begins.
seed = mesh.nearest_triangle(pv.Vec3(0, 0, 100))
selection = mesh.select_linked_by_face_angle(seed.triangle_id, 30.0)

# The general selection becomes a conformal surface only here, where the open-disk rules are checked.
surface = selection.to_triangle_mesh_surface(u_axis_hint=pv.Vec3(1, 0, 0))
cell_map = mm.cell_map_from_surface(surface, cells=(12, 12, 1), height=3.0)
root = mm.gyroid(cell_map, wall_thickness=0.55)

viz.Render(root)
