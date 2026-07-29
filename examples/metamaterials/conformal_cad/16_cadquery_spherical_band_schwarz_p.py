"""Map a Schwarz-P TPMS across a CadQuery-authored spherical band."""

import cadquery as cq

import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz


# Limit the sphere to an open band so its spherical face can carry the lattice.
cad = cq.Workplane(
    obj=cq.Solid.makeSphere(
        22.0,
        angleDegrees1=-60.0,
        angleDegrees2=60.0,
    )
)
surface = pv.CADModel.from_cadquery(cad.faces("%SPHERE")).faces[0]

# Map one Schwarz-P sheet layer across the band, 4.5 mm along the face normal.
cell_map = mm.cell_map_from_cad_face(
    surface,
    cells=(14, 7, 1),
    height=4.5,
)
root = mm.schwarz_p(cell_map, wall_thickness=0.45)

viz.Render(root)
