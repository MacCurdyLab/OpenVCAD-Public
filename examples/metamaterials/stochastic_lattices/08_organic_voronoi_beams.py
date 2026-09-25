"""Round Voronoi beam junctions with member-to-member blending."""

# OpenVCAD
import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz


host = pv.RectPrism(
    pv.Vec3(0.0, 0.0, 0.0),
    pv.Vec3(84.0, 24.0, 18.0),
)
host.prepare(pv.Vec3(0.35, 0.35, 0.35), 1.0)
points = mm.sample_points_in_host(
    host,
    spacing=5.8,
    seed=81,
    max_count=76,
    relaxation=2,
    boundary_clearance=0.8,
)


def build_lattice(member_blend_radius):
    return mm.voronoi_graph_lattice(
        host,
        points,
        beam_thickness=1.0,
        boundary="open",
        member_blend_radius=member_blend_radius,
    )


# The blend radius acts only where distinct struts meet. It does not blur the
# free spans or change how the lattice is confined by the rectangular host.
root = build_lattice(0.4)

viz.Render(root)
