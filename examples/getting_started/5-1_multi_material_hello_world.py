import pyvcad as pv
import pyvcad_rendering as viz

materials = pv.default_materials

# Create two overlapping spheres
radius = 5
left_sphere  = pv.Sphere(pv.Vec3(-radius/2, 0, 0), radius, materials.id("red"))
right_sphere = pv.Sphere(pv.Vec3(+radius/2, 0, 0), radius, materials.id("blue"))

# Perform boolean operation
root = pv.Union()
root.add_child(left_sphere)
root.add_child(right_sphere)

viz.Render(root, materials)