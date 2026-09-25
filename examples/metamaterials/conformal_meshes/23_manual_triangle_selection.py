"""Build a conformal lattice on an explicitly listed triangle patch."""

import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz


# A cube is represented by 12 indexed triangles. IDs 2 and 3 are its upward-facing top.
vertices = [
    pv.Vec3(0, 0, 0),
    pv.Vec3(20, 0, 0),
    pv.Vec3(20, 20, 0),
    pv.Vec3(0, 20, 0),
    pv.Vec3(0, 0, 10),
    pv.Vec3(20, 0, 10),
    pv.Vec3(20, 20, 10),
    pv.Vec3(0, 20, 10),
]
triangles = [
    (0, 2, 1), (0, 3, 2), (4, 5, 6), (4, 6, 7),
    (0, 1, 5), (0, 5, 4), (1, 2, 6), (1, 6, 5),
    (2, 3, 7), (2, 7, 6), (3, 0, 4), (3, 4, 7),
]
mesh = pv.SurfaceMesh(vertices, triangles)
selection = mesh.select_triangles([2, 3])

# Conformal topology is checked here, not when the broadly reusable selection is created.
surface = selection.to_triangle_mesh_surface()
cell_map = mm.cell_map_from_surface(surface, cells=(5, 5, 1), height=2.5)
root = mm.gyroid(cell_map, wall_thickness=0.45)

viz.Render(root)
