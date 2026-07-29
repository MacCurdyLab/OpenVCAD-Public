"""Combine a discrete strut-family override with a gradient along every strut."""

import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz

cell_map = mm.rectangular_cell_map(
    (pv.Vec3(-18.0, -18.0, -12.0), pv.Vec3(18.0, 18.0, 12.0)),
    cells=(4, 4, 3),
)
root = mm.octet(cell_map, beam_radius=0.65, node_radius=0.8)

# Every strut starts with the lower stiffness value.
root.set_attribute(pv.DefaultAttributes.MODULUS, pv.FloatAttribute(1200.0))

# Select reusable strut families that have a large vertical component. Their
# higher modulus repeats in every cell as a discrete load-path allocation.
steep = root.struts.where(lambda strut: abs(strut.direction.z) > 0.55)
steep.set_attribute(pv.DefaultAttributes.MODULUS, pv.FloatAttribute(2800.0))

# component_parameter runs from 0 to 1 along each individual strut. Mapping it
# to 0.6-1.8 creates the same axial gradient on every repeated beam.
root.set_attribute(pv.DefaultAttributes.TOUGHNESS, pv.FloatAttribute(0.6))
root.struts.set_attribute(
    pv.DefaultAttributes.TOUGHNESS,
    root.component_parameter.map_range(0.0, 1.0, 0.6, 1.8),
)

viz.Render(root)
