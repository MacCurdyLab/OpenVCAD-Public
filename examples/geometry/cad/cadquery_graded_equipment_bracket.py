"""Author a parametric equipment bracket in CadQuery and grade its stiffness."""

import cadquery as cq

import pyvcad as pv
import pyvcad_rendering as viz

# These controls size the mounting hardware and the OpenVCAD modulus field.
base_length = 64.0
base_width = 36.0
base_thickness = 5.0
upright_height = 48.0
upright_thickness = 6.0
mounting_hole_diameter = 6.0
mounting_hole_spacing = 42.0
modulus_min = 1200.0
modulus_max = 4200.0

base = (
    cq.Workplane("XY")
    .box(base_length, base_width, base_thickness)
    .faces(">Z")
    .workplane()
    .pushPoints(
        [
            (-mounting_hole_spacing / 2.0, 0.0),
            (mounting_hole_spacing / 2.0, 0.0),
        ]
    )
    .hole(mounting_hole_diameter)
)
upright = (
    cq.Workplane("XY")
    .box(upright_thickness, base_width, upright_height)
    .translate(
        (
            base_length / 2.0 - upright_thickness / 2.0,
            0.0,
            upright_height / 2.0,
        )
    )
)
cadquery_part = base.union(upright)

root = pv.CADModel.from_cadquery(cadquery_part).to_node(use_fast_mode=True)
modulus_expr = (
    f"{modulus_min} + ({modulus_max} - {modulus_min}) "
    f"* clamp(z / {upright_height}, 0, 1)"
)
root.set_attribute(pv.DefaultAttributes.MODULUS, pv.FloatAttribute(modulus_expr))

viz.Render(root)
