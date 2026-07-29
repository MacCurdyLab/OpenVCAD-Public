"""Geometry grading: vary graph-lattice beam radius across a block."""

import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz

cell_map = mm.rectangular_cell_map(
    (pv.Vec3(-22.0, -22.0, -22.0), pv.Vec3(22.0, 22.0, 22.0)),
    cells=(4, 4, 4),
)

beam_radius = pv.FloatAttribute("0.3 + (x + 22.0) / 44.0")
root = mm.bcc(cell_map, beam_radius=beam_radius)
viz.Render(root)
