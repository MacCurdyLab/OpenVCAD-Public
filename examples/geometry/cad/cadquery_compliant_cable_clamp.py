"""Author a parametric cable clamp in CadQuery and grade its stiffness."""

import cadquery as cq

import pyvcad as pv
import pyvcad_rendering as viz

# The same dimensions define the closed clamp body and the modulus transition.
cable_radius = 7.0
wall_thickness = 3.0
clamp_width = 12.0
opening_width = 8.0
opening_depth = 10.0
modulus_min = 450.0
modulus_max = 2200.0

outer_radius = cable_radius + wall_thickness
ring = (
    cq.Workplane("XY")
    .circle(outer_radius)
    .circle(cable_radius)
    .extrude(clamp_width)
)
opening = (
    cq.Workplane("XY")
    .center(outer_radius - opening_depth / 2.0, 0.0)
    .rect(opening_depth, opening_width)
    .extrude(clamp_width)
)
cadquery_part = ring.cut(opening)

root = pv.CADModel.from_cadquery(cadquery_part).to_node(use_fast_mode=True)
modulus_expr = (
    f"{modulus_min} + ({modulus_max} - {modulus_min}) "
    f"* clamp((x + {outer_radius}) / {2.0 * outer_radius}, 0, 1)"
)
root.set_attribute(pv.DefaultAttributes.MODULUS, pv.FloatAttribute(modulus_expr))

viz.Render(root)
