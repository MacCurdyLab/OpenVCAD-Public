"""Compare open and closed boundary products in hosts with an internal cavity."""

# OpenVCAD
import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz


def cavity_host(center_x):
    outer = pv.RectPrism(
        pv.Vec3(center_x, 0.0, 0.0),
        pv.Vec3(24.0, 20.0, 20.0),
    )
    cavity = pv.Sphere(pv.Vec3(center_x, 0.0, 0.0), 5.5)
    host = pv.Difference(outer, cavity)
    host.prepare(pv.Vec3(0.4, 0.4, 0.4), 1.0)
    return host


open_host = cavity_host(-14.0)
closed_host = cavity_host(14.0)
open_points = mm.sample_points_in_host(
    open_host, spacing=5.0, seed=31, max_count=34, boundary_clearance=0.6
)
closed_points = mm.sample_points_in_host(
    closed_host, spacing=5.0, seed=31, max_count=34, boundary_clearance=0.6
)

open_lattice = mm.voronoi_graph_lattice(
    open_host,
    open_points,
    beam_thickness=0.9,
    boundary="open",
)
closed_lattice = mm.voronoi_graph_lattice(
    closed_host,
    closed_points,
    beam_thickness=0.9,
    boundary="closed",
)

# Boundary products become available after preparation. Both modes produce a valid
# implicit solid, while closed mode also records the caps made at host intersections.
open_lattice.prepare(pv.Vec3(0.4, 0.4, 0.4), 1.0)
closed_lattice.prepare(pv.Vec3(0.4, 0.4, 0.4), 1.0)
closed_caps = closed_lattice.boundary_caps()
print(f"Open cap records: {len(open_lattice.boundary_caps())}")
print(f"Closed cap records: {len(closed_caps)}")

root = pv.BBoxUnion([open_lattice, closed_lattice])
viz.Render(root)

