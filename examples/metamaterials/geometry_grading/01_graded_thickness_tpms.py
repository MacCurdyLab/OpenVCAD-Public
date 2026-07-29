"""Geometry grading: vary TPMS wall thickness across a block."""

import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz

block = 48.0
cell_map = mm.rectangular_cell_map(
    (pv.Vec3(-24.0, -10.0, -10.0), pv.Vec3(24.0, 10.0, 10.0)),
    cells=(6, 3, 3),
)

wall_thickness = pv.FloatAttribute("0.6 + 2.0 * (x + 24.0) / 48.0")
root = mm.gyroid(cell_map, wall_thickness=wall_thickness)
viz.Render(root)
