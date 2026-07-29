"""Intersect mapped architected materials with ordinary OpenVCAD geometry."""

import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz

gyroid_map = mm.rectangular_cell_map(
    (pv.Vec3(-17.0, -17.0, -17.0), pv.Vec3(17.0, 17.0, 17.0)),
    cells=(4, 4, 4),
)
gyroid_ball = pv.Intersection(
    mm.gyroid(gyroid_map, wall_thickness=1.4),
    pv.Sphere(pv.Vec3(0.0, 0.0, 0.0), 16.0),
)

octet_map = mm.rectangular_cell_map(
    (pv.Vec3(-15.0, -15.0, -15.0), pv.Vec3(15.0, 15.0, 15.0)),
    cells=(3, 3, 3),
)
octet_box = pv.Intersection(
    mm.octet(octet_map, beam_radius=0.9),
    pv.RectPrism(pv.Vec3(0.0, 0.0, 0.0), pv.Vec3(30.0, 30.0, 30.0)),
)

root = pv.Union(
    pv.Translate(-24.0, 0.0, 0.0, gyroid_ball),
    pv.Translate(24.0, 0.0, 0.0, octet_box),
)
viz.Render(root)
