"""Grade Delaunay beam thickness and joint radius through a cylindrical host."""

# OpenVCAD
import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz


host = pv.Cylinder(pv.Vec3(0.0, 0.0, 0.0), 10.0, 28.0)
host.prepare(pv.Vec3(0.35, 0.35, 0.35), 1.0)
points = mm.sample_points_in_host(
    host,
    spacing=4.5,
    seed=22,
    max_count=46,
    relaxation=1,
    boundary_clearance=0.5,
)

# Both expressions use world-space z. Beams and joints start fine at the bottom
# and grow toward the top of the 28 mm cylinder.
beam_thickness = pv.FloatAttribute("0.55 + 0.035 * (z + 14)").clamp(0.55, 1.55)
node_radius = pv.FloatAttribute("0.42 + 0.03 * (z + 14)").clamp(0.42, 1.28)
root = mm.delaunay_graph_lattice(
    host,
    points,
    beam_thickness=beam_thickness,
    node_radius=node_radius,
    mode="mesh_edges",
    boundary="closed",
)

viz.Render(root)

