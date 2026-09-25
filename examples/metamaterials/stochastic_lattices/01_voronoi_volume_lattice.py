"""Grade Voronoi cell size from left to right inside a rectangular host."""

# OpenVCAD
import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz


host = pv.RectPrism(
    pv.Vec3(0.0, 0.0, 0.0),
    pv.Vec3(90.0, 22.0, 18.0),
)
host.prepare(pv.Vec3(0.4, 0.4, 0.4), 1.0)

# Low density on the left produces large cells. Higher density on the right
# produces more seeds and therefore smaller cells. Density is points per mm^3.
point_density = pv.FloatAttribute(
    "0.0006 + 0.0000048 * (x + 45) * (x + 45)"
).clamp(0.0006, 0.04)
points = mm.sample_points_in_host(
    host,
    density=point_density,
    seed=12,
    max_count=195,
    relaxation=1,
    boundary_clearance=0.5,
)

root = mm.voronoi_graph_lattice(
    host,
    points,
    beam_thickness=0.9,
    node_radius=0.6,
    boundary="closed",
)

left_count = sum(point.x < 0.0 for point in points)
right_count = len(points) - left_count
print(f"Seeds on left: {left_count}; seeds on right: {right_count}")
viz.Render(root)
