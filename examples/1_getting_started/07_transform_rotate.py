import pyvcad as pv
import pyvcad_rendering as viz

# A cube that isn't centered at the origin
cube = pv.RectPrism(pv.Vec3(10, 0, 0), pv.Vec3(10, 10, 10))

# Rotate the cube 45 degrees around the Z axis (yaw)
# Syntax: pv.Rotate(pitch, yaw, roll, child_node)
rotated_cube = pv.Rotate(0.0, 45.0, 0.0, cube)

# Union the original and rotated cube to see the difference
root = pv.Union(cube, rotated_cube)

viz.Render(root)
