import pyvcad as pv
import pyvcad_rendering as viz

# A red plate and a blue post.
plate = pv.RectPrism(pv.Vec3(0, 0, 0), pv.Vec3(30, 30, 4))
plate.set_attribute(pv.DefaultAttributes.COLOR_RGBA, pv.Vec4Attribute(0.85, 0.15, 0.1, 1.0))
post = pv.Cylinder(pv.Vec3(0, 0, 9), 4.0, 14.0)
post.set_attribute(pv.DefaultAttributes.COLOR_RGBA, pv.Vec4Attribute(0.1, 0.3, 0.9, 1.0))

# The blend radius is a field: 0 (a sharp seam) on the -y side, rising to 2 mm on the +y side.
# Bounds size the bounding box; the slope bound keeps the result a safe distance.
radius = pv.FloatAttribute("1 + 0.12 * y").clamp(0.0, 2.0)
joint = pv.Union([plate, post], blend_radius=pv.ScalarParameter(radius, minimum=0.0, maximum=2.0, lipschitz=0.12))

# The fillet grows material outside both parts; its colour mixes red and blue by the blend weight.
viz.Render(joint)
