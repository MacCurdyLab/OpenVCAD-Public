"""
Torus Demo - Default torus vs. explicit major/minor radii.

Torus is always centered at the origin; there is no center argument, so use
Translate to move it elsewhere in the scene.
"""
import pyvcad as pv
import pyvcad_rendering as viz

default_torus = pv.Torus()  # major radius 2, minor radius 1

wide_torus = pv.Translate(10.0, 0.0, 0.0, pv.Torus(6.0, 1.5))

root = pv.Union(default_torus, wide_torus)

viz.Render(root)
