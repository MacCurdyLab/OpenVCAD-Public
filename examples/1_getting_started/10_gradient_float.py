import pyvcad as pv
import pyvcad_rendering as viz

cube = pv.RectPrism(pv.Vec3(0, 0, 0), pv.Vec3(10, 10, 50))

# A gradient modulus that increases linearly along Z from 1 to 10 MPa.
# The cube spans z from -25 to +25.
# Formula: 0.18 * z + 5.5 maps z=-25 -> 1.0 and z=+25 -> 10.0
gradient = pv.FloatAttribute("0.18 * z + 5.5")

cube.set_attribute(pv.DefaultAttributes.MODULUS, gradient)

materials = pv.default_materials
root = cube
viz.Render(root, materials)
