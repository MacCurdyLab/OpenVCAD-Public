import pyvcad as pv
import pyvcad_rendering as viz

cube = pv.RectPrism(pv.Vec3(0, 0, 0), pv.Vec3(50, 10, 10))

# Vector4 attributes use math expressions for Red, Green, Blue, and Alpha (opacity).
# Color channels range from 0.0 to 1.0.
# In this example, green (left) transitions to magenta (right) along the X axis.
r_expr = "x/50 + 0.5"
g_expr = "-x/50 + 0.5"
b_expr = "x/50 + 0.5"
a_expr = "1.0"

# Note: The center of the cube is at x=0. The left side is x=-25 and the right is x=25.
# At x=-25: r=0, g=1, b=0 (Solid Green)
# At x= 25: r=1, g=0, b=1 (Solid Magenta)

color_gradient = pv.Vec4Attribute(r_expr, g_expr, b_expr, a_expr)
cube.set_attribute(pv.DefaultAttributes.COLOR_RGBA, color_gradient)

materials = pv.default_materials
root = cube
viz.Render(root, materials)
