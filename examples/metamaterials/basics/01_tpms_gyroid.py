"""Compare map-first gyroid sheet and solid modes."""

import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz

sheet_map = mm.rectangular_cell_map(
    (pv.Vec3(-33.0, -15.0, -15.0), pv.Vec3(-3.0, 15.0, 15.0)),
    cells=(3, 3, 3),
)
solid_map = mm.rectangular_cell_map(
    (pv.Vec3(3.0, -15.0, -15.0), pv.Vec3(33.0, 15.0, 15.0)),
    cells=(3, 3, 3),
)

sheet = mm.gyroid(sheet_map, mode="sheet", wall_thickness=1.6)
solid = mm.gyroid(solid_map, mode="solid", level=0.0)
root = pv.Union(sheet, solid)

viz.Render(root)
