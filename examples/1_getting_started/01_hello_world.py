import pyvcad as pv
import pyvcad_rendering as viz

# A simple rectangular prism object. No materials or attributes defined.
# Create a 20x20x20 cube centered at the origin
radius = 10.0
dimensions = pv.Vec3(radius*2, radius*2, radius*2)
center = pv.Vec3(0, 0, 0)
cube = pv.RectPrism(center, dimensions)

# Set the cube as the root of the geometric tree
root = cube

# Launch the interactive render window
viz.Render(root)
