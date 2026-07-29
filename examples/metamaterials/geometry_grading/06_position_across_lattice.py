"""Geometry grading: vary beam radius across the whole lattice."""

import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz


cell_map = mm.rectangular_cell_map(
    (pv.Vec3(-24.0, -4.0, -16.0), pv.Vec3(24.0, 4.0, 16.0)),
    cells=(6, 1, 4),
)

# With six cells across X, logical X runs from 0 at minimum X to 6 at maximum X.
position_across_lattice = cell_map.logical_position.x
beam_radius = position_across_lattice.map_range(0.0, 6.0, 0.35, 1.25)

root = mm.cubic(cell_map, beam_radius=beam_radius)
viz.Render(root)
