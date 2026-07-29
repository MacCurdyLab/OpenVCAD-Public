import pyvcad as pv
import pyvcad_rendering as viz

# Define a cylinder we will use multiple times
# Syntax: pv.Cylinder(center point, radius, height)
base_cylinder = pv.Cylinder(pv.Vec3(0,0,0), 2.0, 9.0)

# Build a more complex geometric tree using boolean operations
root = pv.Difference(
    pv.Intersection(
        pv.RectPrism(pv.Vec3(0,0,0), pv.Vec3(8,8,8)),
        pv.Sphere(pv.Vec3(0,0,0), 5.5)
    ),
    pv.Union(
        base_cylinder,
        pv.Union(
            # Syntax: pv.Rotate(pitch, yaw, roll, child)
            pv.Rotate(90.0, 0.0, 0.0, base_cylinder), 
            pv.Rotate(0.0, 90.0, 0.0, base_cylinder)
        )
    )
)

viz.Render(root)
