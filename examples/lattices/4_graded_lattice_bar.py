import pyvcad as pv
import pyvcad_rendering as viz

materials = pv.default_materials
red = materials.id("red")
blue = materials.id("blue")
liquid = materials.id("liquid")

box_dims = pv.Vec3(160, 40, 20)
unit_cell_size = pv.Vec3(10,10,10)
strut_diameter = 1.5
unit_cell_type = pv.LatticeType.BodyCenteredCubic

# Create a lattice and fille a rect prism with it
cell = pv.GraphLattice(unit_cell_type, unit_cell_size, strut_diameter, red)
lattice_fill = pv.Tile(cell)
bar = pv.RectPrism(pv.Vec3(0,0,0), box_dims, red)
filled_bar = pv.Intersection(False, [lattice_fill, bar])


# Apply a grading to the lattice. UNCOMMENT ONE OF THE FOLLOWING LINES to pick a grading

fgrade = pv.FGrade(["x/150 + 0.5","-x/150 + 0.5"], [red,blue], False) # Linear crossfade between red and blue

# fgrade = pv.FGrade(["min(max((-x/260)+0.75,0.5),1)", "min(max((x/260)+0.25,0),0.5)"], 
#                    [red,blue], False) # Mechanical crossfade between red(soft) and blue (hard)

# fgrade = pv.FGrade(["min(max(-x/160,0),0.5)", # Hard material
#                     "min(min(max((x+160)/160,0.5),1),min(max(1-x/400,0.8),1))", # Soft material
#                     "min(max(x/400,0),0.2)"], # Liquid material
#                    [red, blue, liquid], False) # Three-material crossfade between hard, soft and softer (with liquid)

fgrade.set_child(filled_bar)
root = fgrade

viz.Render(root, materials)