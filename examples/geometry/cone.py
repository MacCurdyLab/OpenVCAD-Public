"""
Cone Demo - A cone from its aperture half-angle and height.

Cone takes the half-angle in radians. Its tip sits at the origin and the cone
opens downward along -Y to a flat base at y = -height. Wrap it in Rotate or
Translate to place it elsewhere.
"""
import math

import pyvcad as pv
import pyvcad_rendering as viz

height = 12.0

narrow_cone = pv.Cone(math.radians(15.0), height)
wide_cone = pv.Translate(20.0, 0.0, 0.0, pv.Cone(math.radians(35.0), height))

root = pv.Union(narrow_cone, wide_cone)

viz.Render(root)
