# NOTE: you will need to select at least the "high" render preset to see any detail in this example

import pyvcad as pv
import pyvcad_rendering as viz

# Parameters
unit_cell_type = pv.LatticeType.BodyCenteredCubic
unit_cell_size = pv.Vec3(1,1,1)
strut_diameter = 0.1

cell_bcc = pv.GraphLattice(unit_cell_type, unit_cell_size, strut_diameter)
lattice_fill = pv.Tile(cell_bcc) 
openvcad_text = pv.Mesh("../data/3d_models/openvcad_text.stl")
filled_text = pv.Intersection(lattice_fill, openvcad_text)

root = filled_text

viz.Render(root)