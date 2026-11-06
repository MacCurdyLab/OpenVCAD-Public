"""
PolygonRevolve Demo - Revolve a half-profile around an axis.

This example creates a vase-like profile in the XZ plane and revolves it
270 degrees around the Z axis, leaving a cutaway that shows the profile.
"""
import pyvcad as pv
import pyvcad_rendering as viz

# The closing edge from the last point back to the first lies on the axis.
# PolygonRevolve treats that as the revolve centerline, not as a surface seam.
profile = [
    pv.Vec3(0.0, 0.0, -8.0),
    pv.Vec3(7.0, 0.0, -8.0),
    pv.Vec3(10.0, 0.0, -2.0),
    pv.Vec3(6.0, 0.0, 6.0),
    pv.Vec3(0.0, 0.0, 6.0),
]

axis_start = pv.Vec3(0.0, 0.0, -8.0)
axis_end = pv.Vec3(0.0, 0.0, 6.0)
sweep_degrees = 270.0

root = pv.PolygonRevolve(profile, axis_start, axis_end, sweep_degrees)

viz.Render(root)
