"""Geometry grading: repeat a beam-radius pattern inside every cell."""

import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz


cell_map = mm.rectangular_cell_map(
    (pv.Vec3(-24.0, -4.0, -12.0), pv.Vec3(24.0, 4.0, 12.0)),
    cells=(6, 1, 3),
)

# Phase X repeats from 0 to 1 in each cell. Beams become thick at each midpoint.
position_inside_cell = cell_map.unit_cell_phase.x
distance_from_middle = abs(position_inside_cell - 0.5)
beam_radius = distance_from_middle.map_range(0.0, 0.5, 1.25, 0.25)

root = mm.cubic(cell_map, beam_radius=beam_radius)
viz.Render(root)
