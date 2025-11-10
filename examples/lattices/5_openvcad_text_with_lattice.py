import pyvcad as pv
import pyvcad_rendering as viz

materials = pv.default_materials
red = materials.id("red")

# Parameters
unit_cell_type = pv.LatticeType.BodyCenteredCubic
unit_cell_size = pv.Vec3(1,1,1)
strut_diameter = 0.1

cell_bcc = pv.GraphLattice(unit_cell_type, unit_cell_size, strut_diameter, red)
lattice_fill = pv.Tile(cell_bcc) 
openvcad_text = pv.Mesh("../data/3d_models/openvcad_text.stl", red)
filled_text = pv.Intersection(False, [lattice_fill, openvcad_text])

root = filled_text

viz.Render(root, materials)