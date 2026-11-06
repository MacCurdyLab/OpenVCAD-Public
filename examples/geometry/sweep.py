"""
Sweep Demo - Carry a 2D Profile along a 3D path curve.

Sweep moves the profile along the path in rotation-minimizing frames, so it
does not twist unless asked to. scale and twist may be constants or fields
along the path; twist is in degrees.
"""
import math

import pyvcad as pv
import pyvcad_rendering as viz

path = pv.BSplineCurve.interpolate([(0, 0, 0), (14, 12, 8), (30, 4, 18), (44, 14, 28)])
along = path.length_field(normalized=True)

# A rounded rectangle carried along the spline as is.
plain = pv.Sweep(pv.Profile.rounded_rectangle(8.0, 4.0, 1.0), path)

# The same section, growing to 1.8x and turning half a turn from end to end.
# A field-valued scale needs bounds so the node can size its bounding box.
flared = pv.Sweep(pv.Profile.rounded_rectangle(8.0, 4.0, 1.0), path,
                  scale=pv.ScalarParameter(along.map_range(0.0, 1.0, 1.0, 1.8), minimum=1.0, maximum=1.8),
                  twist=along * 180.0)

# A closed path: a T-section swept around a wavy loop, flange kept facing +Z.
loop = pv.BSplineCurve.interpolate([(14 * math.cos(a), 9 * math.sin(a), 3 * math.sin(2 * a))
                                    for a in (2 * math.pi * i / 24 for i in range(24))], closed=True)
tee = pv.Profile.rectangle(5.0, 1.2, center=(0, 1.9)) | pv.Profile.rectangle(1.2, 4.0)
ring = pv.Sweep(tee, loop, up=(0, 0, 1))

root = pv.Union([plain, pv.Translate(0.0, 30.0, 0.0, flared), pv.Translate(75.0, 15.0, 14.0, ring)])

viz.Render(root)
