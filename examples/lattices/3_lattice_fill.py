import pyvcad as pv
import pyvcad_rendering as viz

materials = pv.default_materials
red = materials.id("red")

sphere_radius = 10
unit_cell_size = pv.Vec3(5,5,5)
strut_diameter = 0.35

# 1. Create a unit cell
cell_bcc = pv.GraphLattice(pv.LatticeType.BodyCenteredCubic, unit_cell_size, strut_diameter, red)

# 2. Use tile node to create a fill
lattice_fill = pv.Tile(cell_bcc) 
# Note. It is not valid to compile/ render lattice_fill directly
# This is because the Tile() node is infinite and needs a parent object to define its bounds

# 3. Create a sphere we will use to fill with the lattice
sphere = pv.Sphere(pv.Vec3(0,0,0), sphere_radius)

# 4. Take the intersection of the sphere and the lattice to create the fill
filled_sphere = pv.Intersection(False, [lattice_fill, sphere])

root = filled_sphere
viz.Render(root, materials)