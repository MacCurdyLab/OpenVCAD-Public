"""Grade legacy eccentricity and wall thickness independently in cell space."""

import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz

use_triangulated = True
u_cells = 6
v_cells = 4
w_cells = 4

eccentricity_lower_bound = 0.8
eccentricity_upper_bound = 1.0
wall_thickness_lower_bound = 0.5
wall_thickness_upper_bound = 2.0

cell_map = mm.rectangular_cell_map(
    (pv.Vec3(-24.0, -18.0, -18.0), pv.Vec3(24.0, 18.0, 18.0)),
    cells=(u_cells, v_cells, w_cells),
)

logical_u = cell_map.logical_position.x
eccentricity = logical_u.map_range(
    0.5,
    u_cells - 0.5,
    eccentricity_lower_bound,
    eccentricity_upper_bound,
)
wall_thickness = logical_u.map_range(
    0.5,
    u_cells - 0.5,
    wall_thickness_lower_bound,
    wall_thickness_upper_bound,
)
root = mm.plate_lattice(
    cell_map,
    wall_thickness=wall_thickness,
    eccentricity=eccentricity,
    surface_mode="triangulated" if use_triangulated else "bilinear",
    surface_tolerance=0.03,
)

viz.Render(root)
