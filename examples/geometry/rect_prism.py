"""
RectPrism Demo - Center/size constructor vs. the FromMinAndMax factory.

RectPrism is a signed-distance leaf primitive: an axis-aligned box. The
regular constructor takes a center point and a full side-length size; the
FromMinAndMax static factory instead builds the same kind of box from its
opposite corners.
"""
import pyvcad as pv
import pyvcad_rendering as viz

centered_box = pv.RectPrism(pv.Vec3(0.0, 0.0, 0.0), pv.Vec3(8.0, 5.0, 4.0))

# An equivalent box built from its corners instead of center + size.
corner_box = pv.RectPrism.FromMinAndMax(
    pv.Vec3(12.0, -2.5, -2.0),
    pv.Vec3(20.0, 2.5, 2.0),
)

root = pv.Union(centered_box, corner_box)

viz.Render(root)
