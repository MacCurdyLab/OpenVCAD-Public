import pyvcad as pv
import pyvcad_rendering as viz

left_sphere = pv.Sphere(pv.Vec3(-3, 0, 0), 5.0)
right_sphere = pv.Sphere(pv.Vec3(3, 0, 0), 5.0)

# Build a combination of the two spheres
root = pv.Union(left_sphere, right_sphere)

# Attributes don't need to be attached exclusively to leaves.
# If we attach an attribute to the parent Union node, it applies to the entire object.
attr = pv.Vec4Attribute("1.0", "0.0", "0.0", "1.0") # Solid Red
root.set_attribute(pv.DefaultAttributes.COLOR_RGBA, attr)

# Notice how the entire object renders red
viz.Render(root, pv.default_materials)
