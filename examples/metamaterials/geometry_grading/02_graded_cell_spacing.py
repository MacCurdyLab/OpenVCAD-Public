"""Geometry grading: redistribute cell spacing across a rectangular map."""

import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz

base_map = mm.rectangular_cell_map(
    (pv.Vec3(-30.0, -12.0, -12.0), pv.Vec3(30.0, 12.0, 12.0)),
    cells=(8, 3, 3),
)

u_spacing = base_map.logical_position.x.map_range(0.0, 8.0, -0.8, 0.8)
warped_map = mm.warp_cell_map(
    base_map,
    u_scale=u_spacing,
    lock_u_bounds=True,
)
root = mm.gyroid(warped_map, wall_thickness=1.4)
viz.Render(root)
