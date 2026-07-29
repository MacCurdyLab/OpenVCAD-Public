"""Render the complete mapped TPMS catalog."""

import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz

block = 24.0
spacing = 30.0
surfaces = []
for index, name in enumerate(mm.TPMS_NAMES):
    center_x = (index - (len(mm.TPMS_NAMES) - 1) / 2.0) * spacing
    cell_map = mm.rectangular_cell_map(
        (
            pv.Vec3(center_x - block / 2.0, -block / 2.0, -block / 2.0),
            pv.Vec3(center_x + block / 2.0, block / 2.0, block / 2.0),
        ),
        cells=(3, 3, 3),
    )
    surfaces.append(mm.tpms(cell_map, name, wall_thickness=1.4))

root = pv.Union(0.0, surfaces)
viz.Render(root)
