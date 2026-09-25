"""Select a smooth imported-mesh patch from a nearby world-space point."""

from pathlib import Path

import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz


tile_path = Path(__file__).resolve().parents[2] / "data" / "3d_models" / "domed_tile.stl"
mesh = pv.SurfaceMesh(str(tile_path), disable_validation=True)

# The query point may be anywhere in space. Its nearest triangle seeds a local-dihedral flood fill;
# smooth curvature grows while the sharp edge around the domed top stops the selection.
seed = mesh.nearest_triangle(pv.Vec3(0, 0, 100))
selection = mesh.select_linked_by_face_angle(
    seed_triangle=seed.triangle_id,
    max_angle_degrees=30.0,
)
surface = selection.to_triangle_mesh_surface()
cell_map = mm.cell_map_from_surface(surface, cells=(12, 12, 1), height=3.0)
root = mm.gyroid(cell_map, wall_thickness=0.55)

viz.Render(root)
