import math

import pyvcad as pv
import pyvcad_rendering as viz

# A tube along a spline whose radius tapers from 3 to 1 mm: a law on arc length is a field built from
# the curve's own length field. A field radius needs bounds so the tube can size its bounding box.
path = pv.BSplineCurve.interpolate([(0, 0, 0), (12, 14, 6), (26, 4, 14), (36, 16, 24)])
taper = path.length_field(normalized=True).map_range(0.0, 1.0, 3.0, 1.0)
horn = pv.Tube(path, pv.ScalarParameter(taper, minimum=1.0, maximum=3.0), end_cap=pv.CapMode.Butt)
# The tube's coordinates are fields too: grade the material along its length.
horn.set_attribute(pv.DefaultAttributes.MODULUS,
                   horn.coordinate_field("normalized_length").map_range(0.0, 1.0, 100.0, 1000.0))

# A closed trefoil knot, graded by the angle around the tube (measured from rotation-minimizing frames).
knot_points = []
for i in range(90):
    a = 2.0 * math.pi * i / 90
    knot_points.append((6.0 * (math.sin(a) + 2.0 * math.sin(2.0 * a)),
                        6.0 * (math.cos(a) - 2.0 * math.cos(2.0 * a)),
                        -6.0 * math.sin(3.0 * a)))
knot_curve = pv.BSplineCurve.interpolate(knot_points, closed=True)
knot = pv.Tube(knot_curve, 2.2)
knot.set_attribute(pv.DefaultAttributes.MODULUS,
                   knot.coordinate_field("angle").map_range(0.0, 360.0, 100.0, 1000.0))

# Distance to a curve as a field: a plate that is stiffer near a path drawn across it.
rib = pv.BSplineCurve.interpolate([(-20, -15, 0), (-5, 0, 0), (5, -5, 0), (20, 15, 0)])
plate = pv.RectPrism(pv.Vec3(0, 0, 0), pv.Vec3(44, 34, 2))
plate.set_attribute(pv.DefaultAttributes.MODULUS,
                    rib.distance_field().map_range(0.0, 8.0, 1000.0, 100.0, clamp=True))

root = pv.Union([horn, pv.Translate(70, 8, 12, knot), pv.Translate(125, 8, 0, plate)])

viz.Render(root)
