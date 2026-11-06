"""Find walls too thin to print with a local-thickness analysis."""

import pyvcad as pv
import pyvcad_rendering as viz

# An open tray: the left wall is 0.8 mm, the front and back walls 1.5 mm, the right wall
# 3 mm and the floor 0.6 mm.
outer = pv.RectPrism(pv.Vec3(0.0, 0.0, 0.0), pv.Vec3(30.0, 20.0, 10.0))
pocket = pv.RectPrism(pv.Vec3(-1.1, 0.0, 0.8), pv.Vec3(26.2, 17.0, 10.4))
tray = pv.Difference(outer, pocket)

# Thickness at every point is the diameter of the largest ball that fits there. Regions are
# the walls (not the sharp edges, which every ball misses) thinner than the threshold.
report = pv.local_thickness(tray, 0.1, threshold=1.0)
print(f"thinnest wall {report.minimum:.2f} mm at {report.minimum_location.round(1)}")
for region in report.regions:
    print(f"  {region.minimum:.2f} mm thin, {region.volume:6.1f} mm^3, "
          f"from {region.minimum_corner.round(1)} to {region.maximum_corner.round(1)}")

# The result is an ordinary attribute: colour by it in the viewer, grade material, or feed it
# to geometry operators. In the viewer, pick the thickness attribute, then Display > Range >
# Fixed with Min 1.0 and Flag below min paints the walls thinner than 1 mm in a flag colour.
tray.set_attribute("thickness", report.attribute)
viz.Render(tray)
