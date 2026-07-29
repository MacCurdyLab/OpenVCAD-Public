"""
Mirror Demo - Reflect geometry across coordinate and arbitrary planes.

This scene renders three reflected objects: a box mirrored across x=0, a box
mirrored across the offset plane x=6, and a sphere mirrored across a diagonal
plane through the origin. Only the reflected geometry is shown.

Mirror returns only the reflected child. To keep both the source and reflection,
combine them explicitly: pv.Union(source, pv.Mirror("x", source)).
"""
import pyvcad as pv
import pyvcad_rendering as viz

# Axis plane: reflects the +X box across x=0, placing the result at -X.
axis_source = pv.RectPrism(pv.Vec3(5.0, -8.0, 0.0), pv.Vec3(2.0, 3.0, 3.0))
axis_reflection = pv.Mirror("x", axis_source)

# Offset plane: reflects across x=6, moving the source from x=10 to x=2.
offset_source = pv.RectPrism(pv.Vec3(10.0, 0.0, 0.0), pv.Vec3(2.0, 3.0, 3.0))
offset_reflection = pv.Mirror("x", 6.0, offset_source)

# Arbitrary plane: the plane through the origin with normal (1, -1, 0)
# swaps the x and y coordinates of this sphere's center.
arbitrary_source = pv.Sphere(pv.Vec3(8.0, 4.0, 0.0), 1.5)
arbitrary_reflection = pv.Mirror(
    pv.Vec3(0.0, 0.0, 0.0),
    pv.Vec3(1.0, -1.0, 0.0),
    arbitrary_source,
)

root = pv.Union(axis_reflection, pv.Union(offset_reflection, arbitrary_reflection))

viz.Render(root)
