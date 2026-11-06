"""Measure channel sizes in the empty space, for example to check that resin can drain."""

import pyvcad as pv
import pyvcad_rendering as viz

# A block with three drain channels along X: 0.6, 1.2 and 2.0 mm across.
block = pv.RectPrism(pv.Vec3(0.0, 0.0, 0.0), pv.Vec3(20.0, 12.0, 8.0))
channels = pv.Union(0.0, [
    pv.Rotate(0.0, 90.0, 0.0, pv.Cylinder(pv.Vec3(0.0, y, 0.0), radius, 30.0))
    for y, radius in ((-4.0, 0.3), (0.0, 0.6), (4.0, 1.0))
])
part = pv.Difference(block, channels)

# Pore size is the same measure as wall thickness, applied to the empty space inside the
# analysis box (here the part's bounding box): the largest empty ball through each point.
report = pv.pore_size(part, 0.05, threshold=1.0)
for region in report.regions:
    print(f"opening {region.minimum:.2f} mm across near y = {region.location[1]:.1f} mm "
          f"({region.volume:.1f} mm^3)")

# The field lives in the empty space, so view it on a node that fills that space: here the
# channels inside the block.
empty_space = pv.Intersection(block, channels)
empty_space.set_attribute("pore_size", report.attribute)

viz.Render(empty_space)
