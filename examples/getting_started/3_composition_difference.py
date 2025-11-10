import pyvcad as pv
import pyvcad_rendering as viz

materials = pv.default_materials

# Create two overlapping spheres
radius = 5
left_sphere  = pv.Sphere(pv.Vec3(-radius/2, 0, 0), radius, materials.id("red"))
right_sphere = pv.Sphere(pv.Vec3(+radius/2, 0, 0), radius, materials.id("red"))

# Perform boolean operation, difference must have exactly two children (A - B)
root = pv.Difference()
root.set_left(left_sphere)
root.set_right(right_sphere)

# Could also do:
# root = pv.Difference(left_sphere, right_sphere)

viz.Render(root, materials)