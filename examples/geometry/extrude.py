"""
Extrude Demo - Turn a 2D Profile into a prism, with optional draft and twist.

Extrude lifts a Profile from the XY plane along +Z by the given height (or
centers it on z=0 with symmetric=True). draft tapers the walls inward by an
angle in degrees and twist turns the section about Z as it rises.
"""
import pyvcad as pv
import pyvcad_rendering as viz

# A rounded plate with a round hole and a slot cut out of the profile.
plate_profile = pv.Profile.rounded_rectangle(36.0, 24.0, 4.0)
plate_profile = plate_profile - pv.Profile.circle(4.0, center=(-9, 0)) - pv.Profile.slot(12.0, 5.0, center=(8, 0), angle=90.0)
plate = pv.Extrude(plate_profile, 6.0)

# A filleted hexagon that narrows by 4 degrees and turns 90 degrees over its height.
hexagon = pv.Profile.regular_polygon(6, 9.0).fillet(1.5)
column = pv.Extrude(hexagon, 30.0, draft=4.0, twist=90.0)

root = pv.Union(plate, pv.Translate(40.0, 0.0, 0.0, column))

viz.Render(root)
