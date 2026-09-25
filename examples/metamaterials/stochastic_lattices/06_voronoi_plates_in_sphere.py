"""Build closed Voronoi cell-wall plates inside a spherical host."""

# OpenVCAD
import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz


host = pv.Sphere(pv.Vec3(0.0, 0.0, 0.0), 11.0)
host.prepare(pv.Vec3(0.4, 0.4, 0.4), 1.0)
points = mm.sample_points_in_host(
    host,
    spacing=4.8,
    seed=44,
    max_count=28,
    relaxation=1,
    boundary_clearance=0.6,
)
root = mm.voronoi_plate_lattice(
    host,
    points,
    wall_thickness=pv.FloatAttribute("0.42 + 0.015 * (z + 11)").clamp(0.42, 0.76),
    boundary="closed",
)

viz.Render(root)
