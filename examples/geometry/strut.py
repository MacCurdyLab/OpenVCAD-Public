"""
Strut Demo - A rod between two points, as a capsule or a capped frustum.

Strut(start, end, radius) is a capsule: a cylinder with spherical ends. The
longer constructor gives each end its own radius and CapMode (Sphere,
HemiSphere or Butt), which makes tapered rods and flat-ended pins.

Here a simple tetrahedral wireframe is wired up by hand from six capsule
edges.
"""
import pyvcad as pv
import pyvcad_rendering as viz

radius = 0.5  # mm

v0 = pv.Vec3(0.0, 0.0, 6.0)
v1 = pv.Vec3(6.0, 0.0, -3.0)
v2 = pv.Vec3(-3.0, 5.2, -3.0)
v3 = pv.Vec3(-3.0, -5.2, -3.0)

edges = [(v0, v1), (v0, v2), (v0, v3), (v1, v2), (v2, v3), (v3, v1)]
wireframe = pv.Union(0.0, [pv.Strut(start, end, radius) for start, end in edges])

# A tapered strut: 2 mm radius with a flat end at the bottom, 0.8 mm with a
# rounded end at the top.
tapered = pv.Strut(pv.Vec3(15.0, 0.0, -4.0), pv.Vec3(15.0, 0.0, 6.0), 2.0, 0.8,
                   pv.CapMode.Butt, pv.CapMode.Sphere)

root = pv.Union(wireframe, tapered)

viz.Render(root)
