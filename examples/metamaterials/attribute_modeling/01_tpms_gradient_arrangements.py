"""Compare whole-map, repeating-cell, and skin/core gradients on one TPMS."""

import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz

cell_map = mm.rectangular_cell_map(
    (pv.Vec3(-24.0, -16.0, -12.0), pv.Vec3(24.0, 16.0, 12.0)),
    cells=(4, 3, 2),
)
root = mm.gyroid(cell_map, wall_thickness=1.8)

# One stiffness gradient crosses the complete TPMS from map U=0 to map U=1.
root.set_attribute(
    pv.DefaultAttributes.MODULUS,
    pv.FloatAttribute("600 + 1800*x"),
    coordinates="map",
)

# This compliance-related pattern restarts from 30 to 80 inside every cell.
root.set_attribute(
    pv.DefaultAttributes.SHORE_HARDNESS,
    pv.FloatAttribute("30 + 50*x"),
    coordinates="cell",
)

# Signed distance d is zero at either exposed TPMS wall surface and negative
# inside the wall. The high-valued skins fade toward the wall's internal core.
root.shell.set_attribute(
    pv.DefaultAttributes.DENSITY,
    pv.FloatAttribute("1200 + 300*cos(3.141592653589793*d/0.9)"),
)

viz.Render(root)
