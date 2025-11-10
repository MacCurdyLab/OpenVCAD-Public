import pyvcad as pv
import pyvcad_rendering as viz

# Load our material config. This provides a mapping between string names 
# and IDs VCAD can use
materials = pv.default_materials

# Creates a 10mm cube centered at 0,0,0
center_point = pv.Vec3(0, 0, 0)
dimensions = pv.Vec3(10,10,10)

root = pv.RectPrism(center_point, dimensions, materials.id("red"))

viz.Render(root, materials) # Render the cube via a pop-up window
