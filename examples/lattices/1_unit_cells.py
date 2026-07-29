import pyvcad as pv
import pyvcad_rendering as viz

unit_cell_size = pv.Vec3(5,5,5)
strut_diameter = 0.5

cell_bcc = pv.GraphLattice(pv.LatticeType.BodyCenteredCubic, unit_cell_size, strut_diameter)
cell_fcc = pv.GraphLattice(pv.LatticeType.FaceCenteredCubic, unit_cell_size, strut_diameter)
cell_cubic = pv.GraphLattice(pv.LatticeType.Cubic, unit_cell_size, strut_diameter)
cell_kelvin = pv.GraphLattice(pv.LatticeType.KelvinCell, unit_cell_size, strut_diameter)

union = pv.BBoxUnion([
    pv.Translate(-9,0,0, cell_bcc),
    pv.Translate(-3,0,0, cell_fcc),
    pv.Translate(3,0,0, cell_cubic),
    pv.Translate(9,0,0, cell_kelvin),
])

root = union
viz.Render(root)