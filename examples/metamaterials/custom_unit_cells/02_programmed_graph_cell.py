"""Generate a parameterized graph cell with ordinary Python loops."""

import itertools

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


unit_cell = hourglass_cell(hub_offset=0.22)
preview_map = mm.rectangular_cell_map(
    (pv.Vec3(-6.0, -6.0, -6.0), pv.Vec3(6.0, 6.0, 6.0)),
    cells=(1, 1, 1),
)
unit_cell_preview = mm.graph_lattice(
    preview_map,
    unit_cell,
    beam_radius=0.55,
    node_radius=0.7,
)

# The unit-cell recipe stays fixed while this geometric control grows along U.
tiled_map = mm.rectangular_cell_map(
    (pv.Vec3(-24.0, -18.0, -18.0), pv.Vec3(24.0, 18.0, 18.0)),
    cells=(4, 3, 3),
)
beam_radius = tiled_map.logical_position.x.map_range(0.0, 4.0, 0.4, 0.85)
tiled_lattice = mm.graph_lattice(
    tiled_map,
    unit_cell,
    beam_radius=beam_radius,
)

root = tiled_lattice
viz.Render(root)
