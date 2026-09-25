"""Wrap a gyroid through an ideal annular pipe without authoring CAD."""

import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz


pipe_center = pv.Vec3(0.0, 0.0, 0.0)
inner_radius = 18.0
outer_radius = 24.0
height = 42.0

# U wraps around the pipe, V follows its axis, and W crosses its wall.
cell_map = mm.cylindrical_cell_map(
    center=pipe_center,
    inner_radius=inner_radius,
    outer_radius=outer_radius,
    height=height,
    arc_count=20,
    axial_cell_size=7.0,
    radial_cell_size=3.0,
    axis=pv.Vec3(0.0, 0.0, 1.0),
    reference_direction=pv.Vec3(1.0, 0.0, 0.0),
)

root = mm.gyroid(cell_map, wall_thickness=0.75)

viz.Render(root)
