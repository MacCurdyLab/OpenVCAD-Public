import pyvcad as pv
import pyvcad_rendering as viz

left_cube = pv.RectPrism(pv.Vec3(-2.5, 0, 0), pv.Vec3(10, 10, 10))
right_cube = pv.RectPrism(pv.Vec3(2.5, 0, 0), pv.Vec3(10, 10, 10))

# Attach distinct color attributes to the leaves (Solid Red and Solid Blue)
# We are intentionally creating a conflict in the overlapping region
red_attr = pv.Vec4Attribute("1.0", "0.0", "0.0", "1.0")
left_cube.set_attribute(pv.DefaultAttributes.COLOR_RGBA, red_attr)

blue_attr = pv.Vec4Attribute("0.0", "0.0", "1.0", "1.0")
right_cube.set_attribute(pv.DefaultAttributes.COLOR_RGBA, blue_attr)

# Combine the two cubes
root = pv.Union(left_cube, right_cube)

# Notice how the overlap region is completely red, taking its values 
# entirely from the first (left) child without blending.
viz.Render(root, pv.default_materials)
