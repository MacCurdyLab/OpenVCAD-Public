"""
Cylinder Demo - Radius/height primitive, always built standing upright along Z.

Cylinder has no orientation argument of its own; it is always aligned along
the Z-axis and centered at its given center point. To point it in another
direction, wrap it in a Rotate.
"""
import pyvcad as pv
import pyvcad_rendering as viz

radius = 4.0
height = 12.0

upright_cylinder = pv.Cylinder(pv.Vec3(0.0, 0.0, 0.0), radius, height)

# Rotate 90 degrees about X (pitch) to tip a second cylinder onto its side.
lying_cylinder = pv.Translate(
    15.0, 0.0, 0.0,
    pv.Rotate(90.0, 0.0, 0.0, pv.Cylinder(pv.Vec3(0.0, 0.0, 0.0), radius, height)),
)

root = pv.Union(upright_cylinder, lying_cylinder)

viz.Render(root)
