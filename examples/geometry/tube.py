"""
Tube Demo - A round tube of constant or varying radius along a curve.

Tube is the curve-following counterpart of Strut. Its ends use the same
CapMode options (Sphere, HemiSphere, Butt) and closed curves need no caps.
"""
import math

import pyvcad as pv
import pyvcad_rendering as viz

# A helix of constant radius, with flat ends.
helix_points = [(10.0 * math.cos(a), 10.0 * math.sin(a), 3.0 * a)
                for a in (4.0 * math.pi * i / 60 for i in range(61))]
helix = pv.BSplineCurve.interpolate(helix_points)
coil = pv.Tube(helix, 1.5, start_cap=pv.CapMode.Butt, end_cap=pv.CapMode.Butt)

# A closed trefoil knot.
knot_points = []
for i in range(90):
    a = 2.0 * math.pi * i / 90
    knot_points.append((6.0 * (math.sin(a) + 2.0 * math.sin(2.0 * a)),
                        6.0 * (math.cos(a) - 2.0 * math.cos(2.0 * a)),
                        -6.0 * math.sin(3.0 * a)))
knot = pv.Tube(pv.BSplineCurve.interpolate(knot_points, closed=True), 2.2)

# A horn whose radius tapers from 3 mm to 1 mm along its length. A field-valued
# radius needs bounds so the tube can size its bounding box.
path = pv.BSplineCurve.interpolate([(0, 0, 0), (12, 14, 6), (26, 4, 14), (36, 16, 24)])
taper = path.length_field(normalized=True).map_range(0.0, 1.0, 3.0, 1.0)
horn = pv.Tube(path, pv.ScalarParameter(taper, minimum=1.0, maximum=3.0), end_cap=pv.CapMode.Butt)

root = pv.Union([coil, pv.Translate(45.0, 0.0, 18.0, knot), pv.Translate(80.0, -8.0, 6.0, horn)])

viz.Render(root)
