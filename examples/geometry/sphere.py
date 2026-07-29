"""
Sphere Demo - Default unit sphere vs. an explicit center/radius sphere.

Sphere is a signed-distance leaf primitive. With no arguments it creates a
sphere of radius 1 centered at the origin; the explicit constructor takes a
center point and a radius.
"""
import pyvcad as pv
import pyvcad_rendering as viz

unit_sphere = pv.Sphere()  # center (0, 0, 0), radius 1

radius = 6.0
placed_sphere = pv.Sphere(pv.Vec3(15.0, 0.0, 0.0), radius)

root = pv.Union(unit_sphere, placed_sphere)

viz.Render(root)
