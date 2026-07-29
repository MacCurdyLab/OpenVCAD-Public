"""Preserve an architected per-strut gradient on a conformal BCC lattice."""

import cadquery as cq

import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz

# Use the curved side of a 40 mm diameter, 30 mm tall cylinder as the map.
cad = cq.Workplane("XY").circle(20.0).extrude(30.0)
surface = pv.CADModel.from_cadquery(cad.faces("%CYLINDER")).faces[0]
cell_map = mm.cell_map_from_cad_face(
    surface,
    cells=(20, 6, 1),
    height=4.0,
    linear=False,
)
root = mm.bcc(cell_map, beam_radius=0.35, node_radius=0.48)

# Each BCC strut is stiffest at its endpoints and most compliant at midspan.
# The four graded body diagonals form one repeated unit-cell property pattern.
root.set_attribute(pv.DefaultAttributes.MODULUS, pv.FloatAttribute(2500.0))
distance_from_midspan = abs(2.0 * root.component_parameter - 1.0)
root.struts.set_attribute(
    pv.DefaultAttributes.MODULUS,
    distance_from_midspan.map_range(0.0, 1.0, 700.0, 2500.0),
)

viz.Render(root)
