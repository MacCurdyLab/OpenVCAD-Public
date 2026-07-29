"""Author a cylindrical CAD face and map a conformal gyroid onto it."""

import cadquery as cq

import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz

# Make a cylinder, then keep its curved side face as the mapping surface.
cad = cq.Workplane("XY").circle(20.0).extrude(30.0)
surface = pv.CADModel.from_cadquery(cad.faces("%CYLINDER")).faces[0]

# Wrap a 24-by-10 gyroid sheet around the face, 4 mm along its normal.
cell_map = mm.cell_map_from_cad_face(
    surface,
    cells=(24, 10, 1),
    height=4.0,
    linear=False,
)
# The gyroid is the repeated open-sheet structure placed by the cell map.
root = mm.gyroid(cell_map, wall_thickness=0.65)

viz.Render(root)
