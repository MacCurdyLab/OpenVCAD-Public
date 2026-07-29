"""Map an octet lattice between two CadQuery-authored cylindrical faces."""

import cadquery as cq

import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz

# These two cylindrical side faces bound the shell that will contain the lattice.
inner_cad = cq.Workplane("XY").circle(15.0).extrude(30.0)
outer_cad = cq.Workplane("XY").circle(22.0).extrude(30.0)
inner = pv.CADModel.from_cadquery(inner_cad.faces("%CYLINDER")).faces[0]
outer = pv.CADModel.from_cadquery(outer_cad.faces("%CYLINDER")).faces[0]

# Fill the gap with 24-by-10-by-3 octet cells instead of offsetting one face.
cell_map = mm.cell_map_between_cad_faces(inner, outer, cells=(24, 10, 3))

# Grow the octet beams from the inner face (0.15 mm) to the outer face (0.25 mm).
beam_radius = cell_map.logical_position.z.map_range(0.0, 3.0, 0.15, 0.25)
root = mm.octet(
    cell_map,
    beam_radius=beam_radius,
)
viz.Render(root)
