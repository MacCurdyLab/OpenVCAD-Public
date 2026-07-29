"""Fill a cylindrical shell with Schwarz-P below and octet beams above."""

import cadquery as cq

import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz


# The two cylinder walls define the curved shell that the lattice will fill.
inner_cad = cq.Workplane("XY").circle(15.0).extrude(30.0)
outer_cad = cq.Workplane("XY").circle(26.0).extrude(30.0)
inner = pv.CADModel.from_cadquery(inner_cad.faces("%CYLINDER")).faces[0]
outer = pv.CADModel.from_cadquery(outer_cad.faces("%CYLINDER")).faces[0]
# One map spans from the inner face to the outer face, keeping both patterns aligned.
cell_map = mm.cell_map_between_cad_faces(
    inner,
    outer,
    cells=(16, 6, 2),
    linear=False,
)

# Build both lattice types in the full shell before clipping them by height.
schwarz_p = mm.schwarz_p(cell_map, wall_thickness=0.75)
octet = mm.octet(cell_map, beam_radius=0.42, node_radius=0.5)

lower_region = pv.RectPrism.FromMinAndMax(
    pv.Vec3(-28.0, -28.0, -4.0),
    pv.Vec3(28.0, 28.0, 15.0),
)
upper_region = pv.RectPrism.FromMinAndMax(
    pv.Vec3(-28.0, -28.0, 15.0),
    pv.Vec3(28.0, 28.0, 34.0),
)
# The lower shell is Schwarz-P; octet beams begin at z = 15 mm.
root = pv.Union(
    pv.Intersection(schwarz_p, lower_region),
    pv.Intersection(octet, upper_region),
)
viz.Render(root)
