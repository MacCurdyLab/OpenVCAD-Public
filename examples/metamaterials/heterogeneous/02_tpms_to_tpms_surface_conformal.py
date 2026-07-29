"""Wrap a gyroid and Schwarz-P sheet around different heights of one cylinder."""

import cadquery as cq

import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz


# This cylinder supplies the curved face that both lattice regions follow.
cad = cq.Workplane("XY").circle(20.0).extrude(30.0)
surface = pv.CADModel.from_cadquery(cad.faces("%CYLINDER")).faces[0]
# One shared map keeps the cell layout continuous around the cylinder.
cell_map = mm.cell_map_from_cad_face(
    surface,
    cells=(16, 6, 1),
    height=8.0,
    linear=False,
)

# Build both sheet patterns over the complete curved map before selecting heights.
gyroid = mm.gyroid(cell_map, wall_thickness=0.7)
schwarz_p = mm.schwarz_p(cell_map, wall_thickness=0.7)

lower_region = pv.RectPrism.FromMinAndMax(
    pv.Vec3(-28.0, -28.0, -4.0),
    pv.Vec3(28.0, 28.0, 15.0),
)
upper_region = pv.RectPrism.FromMinAndMax(
    pv.Vec3(-28.0, -28.0, 15.0),
    pv.Vec3(28.0, 28.0, 34.0),
)
# Keep gyroid below z = 15 mm and Schwarz-P above it for a sharp horizontal join.
root = pv.Union(
    pv.Intersection(gyroid, lower_region),
    pv.Intersection(schwarz_p, upper_region),
)
viz.Render(root)
