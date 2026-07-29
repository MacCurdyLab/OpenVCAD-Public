"""Map a folded plate lattice over a cylinder with normal pre-buckle grading."""

import cadquery as cq

import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz

use_triangulated = True
normal_cells = 10
pre_buckle_min = 0.7
pre_buckle_max = 1.00

cad = cq.Workplane("XY").circle(20.0).extrude(36.0)
surface = pv.CADModel.from_cadquery(cad.faces("%CYLINDER")).faces[0]
cell_map = mm.cell_map_from_cad_face(
    surface,
    cells=(24, 8, normal_cells),
    height=30.0,
    linear=False,
)

pre_buckle = cell_map.logical_position.z.map_range(
    0.5,
    normal_cells - 0.5,
    pre_buckle_min,
    pre_buckle_max,
)
root = mm.plate_lattice(
    cell_map,
    wall_thickness=0.55,
    eccentricity=pre_buckle,
    surface_mode="triangulated" if use_triangulated else "bilinear",
    surface_tolerance=0.04,
)

viz.Render(root)
