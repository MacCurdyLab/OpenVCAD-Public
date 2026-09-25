"""Compare Delaunay triangular plates with Voronoi cell-wall plates."""

# OpenVCAD
import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz


def make_host(center_x):
    host = pv.RectPrism(
        pv.Vec3(center_x, 0.0, 0.0),
        pv.Vec3(22.0, 16.0, 16.0),
    )
    host.prepare(pv.Vec3(0.4, 0.4, 0.4), 1.0)
    return host


delaunay_host = make_host(-13.0)
voronoi_host = make_host(13.0)
delaunay_points = mm.sample_points_in_host(
    delaunay_host, spacing=5.2, seed=17, max_count=23, boundary_clearance=0.5
)
voronoi_points = mm.sample_points_in_host(
    voronoi_host, spacing=5.2, seed=17, max_count=23, boundary_clearance=0.5
)

delaunay_plates = mm.delaunay_plate_lattice(
    delaunay_host,
    delaunay_points,
    wall_thickness=0.5,
    boundary="open",
)
voronoi_plates = mm.voronoi_plate_lattice(
    voronoi_host,
    voronoi_points,
    wall_thickness=0.5,
    boundary="open",
)
root = pv.BBoxUnion([delaunay_plates, voronoi_plates])

print("Delaunay plates are on the left; Voronoi plates are on the right")
viz.Render(root)
