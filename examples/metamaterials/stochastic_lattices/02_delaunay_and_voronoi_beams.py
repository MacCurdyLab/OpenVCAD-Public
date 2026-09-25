"""Compare Delaunay and Voronoi beam networks built from matching seed sets."""

# OpenVCAD
import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz


def make_host(center_x):
    host = pv.RectPrism(
        pv.Vec3(center_x, 0.0, 0.0),
        pv.Vec3(24.0, 18.0, 18.0),
    )
    host.prepare(pv.Vec3(0.4, 0.4, 0.4), 1.0)
    return host


voronoi_host = make_host(-14.0)
delaunay_host = make_host(14.0)
voronoi_points = mm.sample_points_in_host(
    voronoi_host, spacing=5.2, seed=8, max_count=28, boundary_clearance=0.5
)
delaunay_points = mm.sample_points_in_host(
    delaunay_host, spacing=5.2, seed=8, max_count=28, boundary_clearance=0.5
)

voronoi = mm.voronoi_graph_lattice(
    voronoi_host,
    voronoi_points,
    beam_thickness=0.8,
    node_radius=0.55,
)
delaunay = mm.delaunay_graph_lattice(
    delaunay_host,
    delaunay_points,
    beam_thickness=0.8,
    node_radius=0.55,
    mode="mesh_edges",
)
root = pv.BBoxUnion([voronoi, delaunay])

print("Voronoi is shown on the left; Delaunay is shown on the right")
viz.Render(root)

