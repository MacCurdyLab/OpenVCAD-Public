import pyvcad as pv
import pyvcad_rendering as viz

# Syntax: pv.Sphere(center point, radius)
left_sphere = pv.Sphere(pv.Vec3(-3, 0, 0), 5.0)
right_sphere = pv.Sphere(pv.Vec3(3, 0, 0), 5.0)

# The union node combines the two spheres into one continuous object
root = pv.Union(left_sphere, right_sphere)

# You can also pass children directly to the constructor in a list
# root = pv.Union(False, [left_sphere, right_sphere])

viz.Render(root)
