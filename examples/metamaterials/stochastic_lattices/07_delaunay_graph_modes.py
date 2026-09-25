"""Compare the three graph networks available from a Delaunay tessellation."""

# OpenVCAD
import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz


def make_lattice(center_x, mode):
    host = pv.RectPrism(
        pv.Vec3(center_x, 0.0, 0.0),
        pv.Vec3(20.0, 16.0, 16.0),
    )
    host.prepare(pv.Vec3(0.4, 0.4, 0.4), 1.0)
    points = mm.sample_points_in_host(
        host,
        spacing=5.8,
        seed=26,
        max_count=17,
        boundary_clearance=0.5,
    )
    return mm.delaunay_graph_lattice(
        host,
        points,
        beam_thickness=0.72,
        node_radius=0.48,
        mode=mode,
    )


mesh_edges = make_lattice(-22.0, "mesh_edges")
vertex_centroid = make_lattice(0.0, "vertex_centroid")
dual = make_lattice(22.0, "dual")
root = pv.BBoxUnion([mesh_edges, vertex_centroid, dual])

print("Left to right: mesh_edges, vertex_centroid, dual")
viz.Render(root)

