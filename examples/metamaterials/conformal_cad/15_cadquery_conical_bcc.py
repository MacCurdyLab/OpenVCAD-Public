"""Author a conical frustum in CadQuery and map a BCC beam lattice onto it."""

import cadquery as cq

import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz


# Loft two circles to make a tapered wall, then select that conical face.
cad = (
    cq.Workplane("XY")
    .circle(18.0)
    .workplane(offset=32.0)
    .circle(10.0)
    .loft(combine=True, ruled=True)
)
surface = pv.CADModel.from_cadquery(cad.faces("%CONE")).faces[0]

# Bend one BCC layer over the tapered wall, extending 3 mm from the face.
cell_map = mm.cell_map_from_cad_face(
    surface,
    cells=(24, 10, 1),
    height=3.0,
)
root = mm.bcc(cell_map, beam_radius=0.22, node_radius=0.28)

viz.Render(root)
