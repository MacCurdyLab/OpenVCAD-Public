"""Geometry grading: alternate wall thickness from cell to cell."""

import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz


cell_map = mm.rectangular_cell_map(
    (pv.Vec3(-24.0, -4.0, -4.0), pv.Vec3(24.0, 4.0, 4.0)),
    cells=(6, 1, 1),
)

# Cell index X is 0, 1, 2, ... across the strip. This expression returns 0, 1, 0, 1, ...
cell_number = cell_map.cell_index.x
even_or_odd = pv.DerivedFloatAttribute(
    "cell - 2 * floor(cell / 2)",
    {"cell": cell_number},
)
wall_thickness = even_or_odd.map_range(0.0, 1.0, 0.3, 1.8)

root = mm.gyroid(cell_map, wall_thickness=wall_thickness)
viz.Render(root)
