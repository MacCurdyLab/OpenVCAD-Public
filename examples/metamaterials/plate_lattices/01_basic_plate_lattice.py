"""Build a native smooth folded plate lattice in a rectangular cell map."""

import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz

use_triangulated = True

cell_map = mm.rectangular_cell_map(
    (pv.Vec3(-18.0, -18.0, -18.0), pv.Vec3(18.0, 18.0, 18.0)),
    cells=(4, 4, 4),
)
root = mm.plate_lattice(
    cell_map,
    wall_thickness=0.9,
    eccentricity=0.85,
    surface_mode="triangulated" if use_triangulated else "bilinear",
)

viz.Render(root)
