"""Build a planar plate lattice with a Z gradient in pre-buckle."""

import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz

use_triangulated = True
z_cells = 5
pre_buckle_min = 0.75
pre_buckle_max = 1.00

cell_map = mm.rectangular_cell_map(
    (pv.Vec3(-24.0, -18.0, -18.0), pv.Vec3(24.0, 18.0, 18.0)),
    cells=(6, 4, z_cells),
)

pre_buckle = cell_map.logical_position.z.map_range(
    0.5,
    z_cells - 0.5,
    pre_buckle_min,
    pre_buckle_max,
)
root = mm.plate_lattice(
    cell_map,
    wall_thickness=0.75,
    eccentricity=pre_buckle,
    surface_mode="triangulated" if use_triangulated else "bilinear",
    surface_tolerance=0.03,
)

viz.Render(root)
