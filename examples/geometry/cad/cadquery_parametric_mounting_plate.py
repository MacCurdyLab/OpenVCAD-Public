"""Author a parametric mounting plate in CadQuery and grade it in OpenVCAD."""

import cadquery as cq

import pyvcad as pv
import pyvcad_rendering as viz

# These shared parameters control both the CAD part and its stiffness gradient.
plate_length = 48.0
plate_width = 30.0
plate_thickness = 4.0
boss_length = 28.0
boss_width = 14.0
boss_height = 8.0
hole_diameter = 6.0
modulus_min = 800.0
modulus_max = 2800.0

cadquery_part = (
    cq.Workplane("XY")
    .box(plate_length, plate_width, plate_thickness)
    .faces(">Z")
    .workplane()
    .rect(boss_length, boss_width)
    .extrude(boss_height)
    .faces(">Z")
    .workplane()
    .hole(hole_diameter)
)

cad_model = pv.CADModel.from_cadquery(cadquery_part)
root = cad_model.to_node(use_fast_mode=True)
modulus_expr = (
    f"{modulus_min} + ({modulus_max} - {modulus_min}) "
    f"* ((x + {plate_length / 2.0}) / {plate_length})"
)
root.set_attribute(pv.DefaultAttributes.MODULUS, pv.FloatAttribute(modulus_expr))

viz.Render(root)
