"""Reuse custom graph and implicit cells on curved CAD cell maps."""

import itertools
import math

import cadquery as cq

import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz


def hourglass_cell(hub_offset=0.22):
    """Return two corner-connected pyramids joined through the cell center."""
    hub_offset = float(hub_offset)
    if not 0.0 < hub_offset < 0.5:
        raise ValueError("hub_offset must lie between 0 and 0.5")

    bottom_corners = [
        pv.Vec3(x, y, 0.0)
        for x, y in itertools.product((0.0, 1.0), repeat=2)
    ]
    top_corners = [
        pv.Vec3(x, y, 1.0)
        for x, y in itertools.product((0.0, 1.0), repeat=2)
    ]
    vertices = bottom_corners + [
        pv.Vec3(0.5, 0.5, 0.5 - hub_offset),
        pv.Vec3(0.5, 0.5, 0.5 + hub_offset),
    ] + top_corners

    lower_hub = 4
    upper_hub = 5
    edges = [(index, lower_hub) for index in range(4)]
    edges += [(lower_hub, upper_hub)]
    edges += [(upper_hub, index) for index in range(6, 10)]
    return pv.GraphUnitCell(vertices, edges)


two_pi = 2.0 * math.pi


def rippled_p(u, v, w):
    """Return the custom periodic scalar field."""
    a = two_pi * u
    b = two_pi * v
    c = two_pi * w
    return (
        math.cos(a)
        + math.cos(b)
        + math.cos(c)
        + 0.35 * math.cos(a + b + c)
    )


def rippled_p_gradient(u, v, w):
    """Return the analytic gradient of the custom scalar field."""
    a = two_pi * u
    b = two_pi * v
    c = two_pi * w
    coupled = -0.35 * two_pi * math.sin(a + b + c)
    return pv.Vec3(
        -two_pi * math.sin(a) + coupled,
        -two_pi * math.sin(b) + coupled,
        -two_pi * math.sin(c) + coupled,
    )


def rippled_p_cell():
    """Return the complete custom periodic implicit cell."""
    return pv.ImplicitUnitCell(
        rippled_p,
        rippled_p_gradient,
        name="rippled_p",
    )


# Make two separated cylinders so both custom cells fit in one interactive view.
graph_cad = (
    cq.Workplane("XY")
    .center(-20.0, 0.0)
    .circle(12.0)
    .extrude(24.0)
)
implicit_cad = (
    cq.Workplane("XY")
    .center(20.0, 0.0)
    .circle(12.0)
    .extrude(24.0)
)
graph_surface = pv.CADModel.from_cadquery(
    graph_cad.faces("%CYLINDER")
).faces[0]
implicit_surface = pv.CADModel.from_cadquery(
    implicit_cad.faces("%CYLINDER")
).faces[0]

# Only the maps change; the complete cell definitions remain in this script.
graph_map = mm.cell_map_from_cad_face(
    graph_surface,
    cells=(16, 8, 1),
    height=3.0,
    linear=False,
)
implicit_map = mm.cell_map_from_cad_face(
    implicit_surface,
    cells=(16, 8, 1),
    height=3.0,
    linear=False,
)

conformal_graph = mm.graph_lattice(
    graph_map,
    hourglass_cell(hub_offset=0.22),
    beam_radius=0.28,
    node_radius=0.34,
)
conformal_implicit = mm.tpms(
    implicit_map,
    rippled_p_cell(),
    wall_thickness=0.6,
)

root = pv.Union(conformal_graph, conformal_implicit)
viz.Render(root)
