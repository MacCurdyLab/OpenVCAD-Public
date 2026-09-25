"""Create a local curved patch by surface distance, then refine it by triangle rings."""

import math

import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz


cells = 20
spacing = 1.5
vertices = []
for y in range(cells + 1):
    for x in range(cells + 1):
        world_x = spacing * (x - cells / 2)
        world_y = spacing * (y - cells / 2)
        world_z = 2.2 * math.sin(world_x / 9.0) * math.cos(world_y / 8.0)
        vertices.append(pv.Vec3(world_x, world_y, world_z))

triangles = []
stride = cells + 1
for y in range(cells):
    for x in range(cells):
        lower_left = y * stride + x
        triangles.append((lower_left, lower_left + 1, lower_left + stride + 1))
        triangles.append((lower_left, lower_left + stride + 1, lower_left + stride))

mesh = pv.SurfaceMesh(vertices, triangles)
seed_vertex = mesh.nearest_vertex(pv.Vec3(0, 0, 20))
local_patch = mesh.select_by_geodesic_radius(seed_vertex, radius=10.0)

# Ring editing is useful for adding clearance or repairing an almost-correct automatic selection.
selection = local_patch.grown(1).shrunk(1)
boundary = selection.boundary_edges()
if not boundary:
    raise RuntimeError("Expected the local patch to have an open boundary")

surface = selection.to_triangle_mesh_surface(u_axis_hint=pv.Vec3(1, 0, 0))
cell_map = mm.cell_map_from_surface(surface, cells=(8, 8, 1), height=2.5)
root = mm.bcc(cell_map, beam_radius=0.28, node_radius=0.32)

viz.Render(root)
