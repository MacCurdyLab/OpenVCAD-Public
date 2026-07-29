import pyvcad as pv
import pyvcad_rendering as viz

cube = pv.RectPrism(pv.Vec3(0, 0, 0), pv.Vec3(10, 10, 10))

# Define a static float attribute with a value of 5.0 (assume MPa)
my_attr = pv.FloatAttribute(5.0)

# Attach the attribute to our cube node.
# We use the default namespace for modulus so the compiler knows what it is.
# You could use a custom string like "my_custom_modulus", but the compiler 
# might ignore it if it doesn't recognize it.
cube.set_attribute(pv.DefaultAttributes.MODULUS, my_attr)

# We must use default_materials even if we don't use Volume Fractions 
# so the renderer knows we have attributes
materials = pv.default_materials
root = cube
viz.Render(root, materials)
