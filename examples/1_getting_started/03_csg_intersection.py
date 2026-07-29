import pyvcad as pv
import pyvcad_rendering as viz

left_sphere = pv.Sphere(pv.Vec3(-3, 0, 0), 5.0)
right_sphere = pv.Sphere(pv.Vec3(3, 0, 0), 5.0)

# The intersection node keeps only the overlapping region
root = pv.Intersection(left_sphere, right_sphere)

# Using constructor syntax: pv.Intersection(False, [left_sphere, right_sphere])
# The 'False' dictates how materials combine, covered later.

viz.Render(root)
