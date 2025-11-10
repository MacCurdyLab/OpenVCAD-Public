import pyvcad as pv
import pyvcad_rendering as viz

materials = pv.default_materials

# Create two overlapping spheres
radius = 5
left_sphere  = pv.Sphere(pv.Vec3(-radius/2, 0, 0), radius, materials.id("red"))
right_sphere = pv.Sphere(pv.Vec3(+radius/2, 0, 0), radius, materials.id("red"))

# Perform boolean operation, in a single line, don't worry about the 'False' for now
root = pv.Intersection(False, [left_sphere, right_sphere])

viz.Render(root, materials)