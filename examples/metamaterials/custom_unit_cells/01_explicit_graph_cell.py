"""Build a custom graph unit cell from an explicit vertex and edge list."""

import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz


# The center connects to matching points on all six unit-cell boundaries.
vertices = [
    pv.Vec3(0.5, 0.5, 0.5),
    pv.Vec3(0.0, 0.5, 0.5),
    pv.Vec3(1.0, 0.5, 0.5),
    pv.Vec3(0.5, 0.0, 0.5),
    pv.Vec3(0.5, 1.0, 0.5),
    pv.Vec3(0.5, 0.5, 0.0),
    pv.Vec3(0.5, 0.5, 1.0),
]
edges = [(0, index) for index in range(1, len(vertices))]
unit_cell = pv.GraphUnitCell(vertices, edges)

# A one-cell map is the quickest way to inspect the normalized graph as geometry.
preview_map = mm.rectangular_cell_map(
    (pv.Vec3(-6.0, -6.0, -6.0), pv.Vec3(6.0, 6.0, 6.0)),
    cells=(1, 1, 1),
)
unit_cell_preview = mm.graph_lattice(
    preview_map,
    unit_cell,
    beam_radius=0.65,
    node_radius=0.8,
)

# Reuse the same cell on a larger map to inspect its periodic connections.
tiled_map = mm.rectangular_cell_map(
    (pv.Vec3(-18.0, -18.0, -18.0), pv.Vec3(18.0, 18.0, 18.0)),
    cells=(3, 3, 3),
)
tiled_lattice = mm.graph_lattice(
    tiled_map,
    unit_cell,
    beam_radius=0.65,
    node_radius=0.8,
)

root = tiled_lattice
viz.Render(root)
