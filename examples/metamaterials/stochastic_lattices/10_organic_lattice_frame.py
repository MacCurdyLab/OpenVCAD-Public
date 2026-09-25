"""Blend organic Voronoi beams into a separate rectangular frame."""

# OpenVCAD
import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz


FRAME_SIZE = (90.0, 24.0, 18.0)
FRAME_RADIUS = 1.35
MEMBER_BLEND_RADIUS = 0.4
ATTACHMENT_BLEND_RADIUS = 0.7

host = pv.RectPrism(
    pv.Vec3(0.0, 0.0, 0.0),
    pv.Vec3(*FRAME_SIZE),
)
host.prepare(pv.Vec3(0.35, 0.35, 0.35), 1.0)
points = mm.sample_points_in_host(
    host,
    spacing=6.0,
    seed=53,
    max_count=80,
    relaxation=2,
    boundary_clearance=0.6,
)


def box_frame(size, radius):
    minimum = tuple(-0.5 * value for value in size)
    maximum = tuple(0.5 * value for value in size)
    corners = [
        pv.Vec3(x, y, z)
        for x in (minimum[0], maximum[0])
        for y in (minimum[1], maximum[1])
        for z in (minimum[2], maximum[2])
    ]
    edges = []
    for first in range(len(corners)):
        for second in range(first + 1, len(corners)):
            differences = sum(
                abs(getattr(corners[first], axis) - getattr(corners[second], axis)) > 1e-6
                for axis in ("x", "y", "z")
            )
            if differences == 1:
                edges.append(pv.Strut(corners[first], corners[second], radius))
    return pv.BBoxUnion(edges)


lattice = mm.voronoi_graph_lattice(
    host,
    points,
    beam_thickness=1.0,
    boundary="open",
    member_blend_radius=MEMBER_BLEND_RADIUS,
)
frame = box_frame(FRAME_SIZE, FRAME_RADIUS)


def build_part(attachment_blend_radius):
    # This Boolean blend is intentionally separate from member blending. It
    # rounds only the places where the completed lattice meets the frame.
    return pv.Union(attachment_blend_radius, [frame, lattice])


root = build_part(ATTACHMENT_BLEND_RADIUS)

viz.Render(root)
