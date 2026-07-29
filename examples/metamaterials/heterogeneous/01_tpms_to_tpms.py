"""Blend gyroid into Schwarz-D across one cell of a shared rectangular map."""

import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz


TRANSITION_HALF_WIDTH_CELLS = 0.5

# This shared map keeps both TPMS patterns aligned cell-for-cell.
cell_map = mm.rectangular_cell_map(
    (pv.Vec3(-24.0, -12.0, -8.0), pv.Vec3(24.0, 12.0, 8.0)),
    cells=(6, 3, 2),
)

# The ramp changes from gyroid (0) to Schwarz-D (1) across the middle cell.
weight = mm.ramp(
    3.0 - TRANSITION_HALF_WIDTH_CELLS,
    3.0 + TRANSITION_HALF_WIDTH_CELLS,
    axis="u",
    coordinates=cell_map.logical_position,
)
# Mix the repeating TPMS patterns before turning them into a printable sheet.
mixed_cell = pv.ImplicitUnitCell.mixed(
    pv.ImplicitUnitCell.standard("gyroid"),
    pv.ImplicitUnitCell.standard("schwarz_d"),
    weight,
)
root = mm.tpms(cell_map, mixed_cell, wall_thickness=1.2)
viz.Render(root)
