import pyvcad as pv
import pyvcad_rendering as viz

blue = pv.default_materials.id("blue")
green = pv.default_materials.id("green")
support = pv.default_materials.id("support")
voxel_size = pv.Vec3(0.0423, 0.0846, 0.027)

radius = 25
obj = pv.Sphere(pv.Vec3(0,0,0), radius, blue)


support_ana = pv.SupportAnalyzerParallel(obj, voxel_size, support)
support_volume = support_ana.analyze()

unit_cell_size = pv.Vec3(1.5,1.5,1.5) # mm
strut_diameter = 0.2 # mm
cell_bcc = pv.GraphLattice(pv.LatticeType.BodyCenteredCubic, unit_cell_size, strut_diameter, green)
lattice_fill = pv.Tile(cell_bcc) 
support_lattice = pv.Intersection(False, [lattice_fill, support_volume])

union = pv.Union(False, [obj, support_lattice, support_volume])

root = union

viz.Render(root, pv.default_materials)
