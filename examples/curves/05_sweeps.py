import math

import pyvcad as pv
import pyvcad_rendering as viz

# A profile swept along a 3D path. The profile rides in the path's rotation-minimizing frames, so it
# does not twist on its own; scale and twist laws along the path are fields built from the path's
# own coordinates.
path = pv.BSplineCurve.interpolate([(0, 0, 0), (14, 12, 8), (30, 4, 18), (44, 14, 28)])
along = path.length_field(normalized=True)
horn = pv.Sweep(pv.Profile.rounded_rectangle(8.0, 4.0, 1.0), path,
                scale=pv.ScalarParameter(along.map_range(0.0, 1.0, 1.0, 1.8), minimum=1.0, maximum=1.8),
                twist=along * 180.0)
horn.set_attribute(pv.DefaultAttributes.MODULUS, horn.coordinate_field("normalized_length").map_range(0.0, 1.0, 100.0, 1000.0))

# A closed path: a wavy elliptical loop swept with a T-shaped section, flange up, graded across
# the section. The frames meet at the seam.
loop = pv.BSplineCurve.interpolate([(14 * math.cos(a), 9 * math.sin(a), 3 * math.sin(2 * a))
                                    for a in (2 * math.pi * i / 24 for i in range(24))], closed=True)
tee = pv.Profile.rectangle(5.0, 1.2, center=(0, 1.9)) | pv.Profile.rectangle(1.2, 4.0)
ring = pv.Sweep(tee, loop, up=(0, 0, 1))
ring.set_attribute(pv.DefaultAttributes.MODULUS, ring.coordinate_field("v").map_range(-2.0, 2.5, 100.0, 1000.0))

root = pv.Union([horn, pv.Translate(75, 8, 14, ring)])

viz.Render(root)
