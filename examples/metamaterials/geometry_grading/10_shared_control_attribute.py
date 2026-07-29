"""Geometry grading: reuse one field as a control and as named data."""

import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz


cell_map = mm.rectangular_cell_map(
    (pv.Vec3(-24.0, -12.0, -8.0), pv.Vec3(24.0, 12.0, 8.0)),
    cells=(6, 3, 2),
)
logical_u = cell_map.logical_position.x
control = ((logical_u / 6.0) ** 2).map_range(0.0, 1.0, 0.55, 1.65)
root = mm.gyroid(cell_map, wall_thickness=control)
root.set_attribute("wall_thickness_control", control)
viz.Render(root)
