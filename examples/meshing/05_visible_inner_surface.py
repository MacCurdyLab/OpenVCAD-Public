"""Pick the inner surface of a vented shell automatically, as seen from points inside it."""

import pyvcad as pv
import pyvcad_rendering as viz

VOXEL_SIZE = 0.5  # mm
OUTER_RADIUS = 60.0  # mm
WALL = 4.0  # mm
VENT_RADIUS = 6.0  # mm

# A dome shell with four round vents near the crown.
ball = pv.Difference(pv.Sphere(pv.Vec3(0, 0, 0), OUTER_RADIUS),
                     pv.Sphere(pv.Vec3(0, 0, 0), OUTER_RADIUS - WALL))
dome = pv.Intersection(ball, pv.RectPrism(pv.Vec3(0, 0, 50), pv.Vec3(150, 150, 100)))
shell = dome
for x, y in ((25, 0), (-25, 0), (0, 25), (0, -25)):
    shell = pv.Difference(shell, pv.Cylinder(pv.Vec3(x, y, 50), VENT_RADIUS, 40.0))
shell_mesh = pv.SurfaceMesh(shell, VOXEL_SIZE)

# Seeds spread through a region under the dome, like points inside a head. A triangle is selected
# when a straight line from a seed reaches it before any other triangle, so the selection crosses
# creases and vent edges but never reaches the outer skin.
head_region = pv.Sphere(pv.Vec3(0, 0, 25), 18.0)
inner = shell_mesh.select_visible_from(head_region, seed_count=8, facing="toward")

print(f"shell: {shell_mesh.triangle_count:,} triangles; inner surface: {inner.triangle_count:,}")
print(f"inner surface area: {inner.area:,.0f} mm^2")

# The result is an ordinary MeshSelection: refine it, combine it, extract it, or review it here.
viz.select_mesh_patch(shell_mesh, initial_selection=inner)
