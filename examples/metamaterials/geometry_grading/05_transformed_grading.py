"""Geometry grading: rotate a lattice and its thickness control together."""

import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz


cell_map = mm.rectangular_cell_map(
    (pv.Vec3(-24.0, -10.0, -10.0), pv.Vec3(24.0, 10.0, 10.0)),
    cells=(6, 3, 3),
)
thickness = pv.FloatAttribute("0.55 + 1.35 * (x + 24.0) / 48.0")
lattice = mm.gyroid(cell_map, wall_thickness=thickness)
root = pv.Rotate(0.0, 0.0, 35.0, lattice)
viz.Render(root)
