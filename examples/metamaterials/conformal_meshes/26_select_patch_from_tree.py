"""Resolve an OpenVCAD tree surface, ray-select one face, and map a lattice onto it."""

import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz


design = pv.RectPrism(pv.Vec3(0, 0, 0), pv.Vec3(20, 20, 10))

# Tree-to-mesh resolution is explicit because changing this value changes the generated triangles
# and therefore their IDs. A directional ray then provides a reproducible top-face seed.
voxel_size = 1.0
mesh = pv.SurfaceMesh(design, voxel_size)
seed = mesh.ray_intersection(pv.Vec3(0, 0, 20), pv.Vec3(0, 0, -1))
if seed is None:
    raise RuntimeError("The selection ray did not intersect the resolved tree surface")

selection = mesh.select_linked_by_face_angle(
    seed_triangle=seed.triangle_id,
    max_angle_degrees=20.0,
)
surface = selection.to_triangle_mesh_surface(u_axis_hint=pv.Vec3(1, 0, 0))
cell_map = mm.cell_map_from_surface(surface, cells=(5, 5, 1), height=2.5)
root = mm.cubic(cell_map, beam_radius=0.30, node_radius=0.34)

viz.Render(root)
