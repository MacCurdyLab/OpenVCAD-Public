"""Select one edge-connected mesh component and map a lattice onto it."""

import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz


# The source contains two disconnected square patches in one SurfaceMesh.
vertices = [
    pv.Vec3(0, 0, 0),
    pv.Vec3(20, 0, 0),
    pv.Vec3(20, 20, 0),
    pv.Vec3(0, 20, 0),
    pv.Vec3(30, 0, 4),
    pv.Vec3(50, 0, 4),
    pv.Vec3(50, 20, 4),
    pv.Vec3(30, 20, 4),
]
triangles = [(0, 1, 2), (0, 2, 3), (4, 5, 6), (4, 6, 7)]
mesh = pv.SurfaceMesh(vertices, triangles)

# Starting from triangle 0 grows through shared edges but cannot cross to the second component.
selection = mesh.select_linked(seed_triangle=0)
surface = selection.to_triangle_mesh_surface()
cell_map = mm.cell_map_from_surface(surface, cells=(5, 5, 1), height=3.0)
root = mm.bcc(cell_map, beam_radius=0.30, node_radius=0.34)

viz.Render(root)
