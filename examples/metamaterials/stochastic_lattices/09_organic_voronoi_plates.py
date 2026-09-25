"""Round the intersections between porous Voronoi cell-wall plates."""

# OpenVCAD
import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz


host = pv.RectPrism(
    pv.Vec3(0.0, 0.0, 0.0),
    pv.Vec3(78.0, 24.0, 18.0),
)
host.prepare(pv.Vec3(0.35, 0.35, 0.35), 1.0)
points = mm.sample_points_in_host(
    host,
    spacing=6.2,
    seed=29,
    max_count=56,
    relaxation=2,
    boundary_clearance=0.8,
)


def build_lattice(member_blend_radius):
    return mm.voronoi_plate_lattice(
        host,
        points,
        wall_thickness=0.6,
        boundary="open",
        member_blend_radius=member_blend_radius,
    )


root = build_lattice(0.28)

viz.Render(root)
