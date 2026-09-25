"""Join mesh vertices with shortest surface paths and select the enclosed patch."""

import math

import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz


cells = 20
spacing = 1.2
vertices = []
for y in range(cells + 1):
    for x in range(cells + 1):
        world_x = spacing * (x - cells / 2)
        world_y = spacing * (y - cells / 2)
        world_z = 1.8 * math.cos(world_x / 7.0) * math.cos(world_y / 7.0)
        vertices.append(pv.Vec3(world_x, world_y, world_z))

triangles = []
stride = cells + 1
for y in range(cells):
    for x in range(cells):
        lower_left = y * stride + x
        triangles.append((lower_left, lower_left + 1, lower_left + stride + 1))
        triangles.append((lower_left, lower_left + stride + 1, lower_left + stride))

mesh = pv.SurfaceMesh(vertices, triangles)

# Four exact mesh vertices define the corners of a closed outline. Shortest paths keep every
# segment on the triangulated surface; their ordered edge lists form the selection delimiter.
def vertex_id(x, y):
    return y * stride + x


corners = [vertex_id(5, 5), vertex_id(15, 5), vertex_id(15, 15), vertex_id(5, 15)]
boundary_edges = []
for index, start in enumerate(corners):
    end = corners[(index + 1) % len(corners)]
    boundary_edges.extend(mesh.shortest_surface_path(start, end).edges)

seed_triangle = 2 * (10 * cells + 10)
selection = mesh.select_enclosed_region(boundary_edges, seed_triangle)
surface = selection.to_triangle_mesh_surface(u_axis_hint=pv.Vec3(1, 0, 0))
cell_map = mm.cell_map_from_surface(surface, cells=(8, 8, 1), height=2.5)
root = mm.cubic(cell_map, beam_radius=0.24, node_radius=0.28)

viz.Render(root)
