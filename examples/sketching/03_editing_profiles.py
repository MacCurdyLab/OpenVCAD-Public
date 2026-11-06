import matplotlib.pyplot as plt

import pyvcad as pv
import pyvcad_rendering as viz

# 1. Patterns: copies of one lobe turned around a hub with an ordinary loop, then webbed together.
#    round_concave() fills every inside corner, whatever curves meet there.
lobes = 5
lobe = pv.Profile.slot(30.0, 9.0, center=(13.0, 0.0))
rotor = pv.Profile.circle(10.0)
for i in range(lobes):
    rotor = rotor | lobe.rotated(360.0 * i / lobes)
rotor = rotor.round_concave(3.0) - pv.Profile.circle(4.0)

# 2. Mirror: sketch half of a symmetric part and reflect it across the Y axis.
#    The quarter arc ends level at the mirror line, so the two halves join smoothly.
half = pv.Sketch((0, 0)).line_to(18, 0).line_to(18, 6).line_to(8, 10).line_to(8, 26).arc_to(0, 34, 8.0).close()
clip = (half.profile() | half.profile().mirrored()) - pv.Profile.circle(3.0, center=(0, 26))

# 3. Pick corners with Python: fillet the top corners of a bracket and chamfer the bottom ones.
bracket = pv.Profile.rectangle(36, 24) - pv.Profile.rectangle(20, 12, center=(0, -6))
top = [c for c in bracket.corners() if c[1] > 0]
bottom = [c for c in bracket.corners() if c[1] <= -12]
bracket = bracket.fillet(5.0, at=top).chamfer(2.0, at=bottom)

# 4. Stitch loose pieces, like an imported drawing whose curves come in any order and direction.
pieces = [
    pv.ArcCurve((0, 0, 0), 14.0, 0.0, 180.0),
    pv.LineSegment((14, -10), (14, 0)),
    pv.LineSegment((-14, -10), (14, -10)),
    pv.LineSegment((-14, 0), (-14, -10)),
]
arch = pv.Profile.from_curves(pieces) - pv.Profile.circle(6.0, center=(0, 0))

# Check all four side by side: plot_profile() draws into any matplotlib axes.
fig, axes = plt.subplots(1, 4, figsize=(16, 4.5))
for ax, profile, name in zip(axes, [rotor, clip, bracket, arch], ["pattern", "mirror", "chosen corners", "stitched"]):
    viz.plot_profile(profile, ax=ax, show=False, title=name)
plt.show()

parts = [pv.Translate(60.0 * i, 0, 0, pv.Extrude(p, 5.0)) for i, p in enumerate([rotor, clip, bracket, arch])]
root = pv.Union(parts)

viz.Render(root)
