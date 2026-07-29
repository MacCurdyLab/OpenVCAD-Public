import pyvcad as pv
import pyvcad_rendering as viz

left_sphere = pv.Sphere(pv.Vec3(-3, 0, 0), 5.0)
right_sphere = pv.Sphere(pv.Vec3(3, 0, 0), 5.0)

# The difference node subtracts the right child from the left child (A - B)
root = pv.Difference()
root.set_left(left_sphere)
root.set_right(right_sphere)

# The difference node has exactly two children.
# You can also use: root = pv.Difference(left_sphere, right_sphere)

viz.Render(root)
