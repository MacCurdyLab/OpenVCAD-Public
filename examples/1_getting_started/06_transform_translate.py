import pyvcad as pv
import pyvcad_rendering as viz

cube = pv.RectPrism(pv.Vec3(0, 0, 0), pv.Vec3(10, 10, 10))

# Move the cube +15mm on the X-axis
# Syntax: pv.Translate(x, y, z, child_node)
translated_cube = pv.Translate(15.0, 0.0, 0.0, cube)

# We can union the original and translated cube to see them both
root = pv.Union(cube, translated_cube)

viz.Render(root)
