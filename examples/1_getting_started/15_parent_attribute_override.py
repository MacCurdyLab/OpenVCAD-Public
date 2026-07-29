import pyvcad as pv
import pyvcad_rendering as viz

left_cube = pv.RectPrism(pv.Vec3(-2.5, 0, 0), pv.Vec3(10, 10, 10))
right_cube = pv.RectPrism(pv.Vec3(2.5, 0, 0), pv.Vec3(10, 10, 10))

red_attr = pv.Vec4Attribute("1.0", "0.0", "0.0", "1.0")
left_cube.set_attribute(pv.DefaultAttributes.COLOR_RGBA, red_attr)

blue_attr = pv.Vec4Attribute("0.0", "0.0", "1.0", "1.0")
right_cube.set_attribute(pv.DefaultAttributes.COLOR_RGBA, blue_attr)

root = pv.Union(left_cube, right_cube)

# Now, we also attach an attribute directly to the parent Union node
# using the EXACT SAME attribution string (COLOR_RGBA)
green_attr = pv.Vec4Attribute("0.0", "1.0", "0.0", "1.0")
root.set_attribute(pv.DefaultAttributes.COLOR_RGBA, green_attr)

# The entire object will render completely green.
# The attribute on the union node OVERRIDES the attributes of the children.
viz.Render(root, pv.default_materials)
