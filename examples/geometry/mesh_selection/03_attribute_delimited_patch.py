"""Stop linked growth at a per-triangle region or attribute discontinuity."""

import math

import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz


cells_x = 18
cells_y = 12
spacing = 1.5
vertices = []
for y in range(cells_y + 1):
    for x in range(cells_x + 1):
        world_x = spacing * (x - cells_x / 2)
        world_y = spacing * (y - cells_y / 2)
        world_z = 0.6 * math.sin(world_y / 6.0)
        vertices.append(pv.Vec3(world_x, world_y, world_z))

triangles = []
region_labels = []
stride = cells_x + 1
for y in range(cells_y):
    for x in range(cells_x):
        lower_left = y * stride + x
        triangles.append((lower_left, lower_left + 1, lower_left + stride + 1))
        triangles.append((lower_left, lower_left + stride + 1, lower_left + stride))
        region = 0 if x < cells_x // 2 else 1
        region_labels.extend((region, region))

mesh = pv.SurfaceMesh(vertices, triangles)

# The integer labels may come from segmentation, material IDs, or any thresholded triangle data.
# Growth crosses smooth faces but stops wherever neighboring labels differ.
selection = mesh.select_linked_constrained(
    seed_triangle=0,
    triangle_regions=region_labels,
)
surface = selection.to_triangle_mesh_surface(u_axis_hint=pv.Vec3(0, 1, 0))
cell_map = mm.cell_map_from_surface(surface, cells=(5, 8, 1), height=1.2)
root = mm.gyroid(cell_map, wall_thickness=0.45)

viz.Render(root)
