import pyvcad as pv
import pyvcad_rendering as viz

# A red plate with a row of blue posts.
plate = pv.RectPrism(pv.Vec3(0, 0, 0), pv.Vec3(80, 20, 4))
plate.set_attribute(pv.DefaultAttributes.COLOR_RGBA, pv.Vec4Attribute(0.85, 0.15, 0.1, 1.0))
posts = []
for x in (-30, -15, 0, 15, 30):
    post = pv.Cylinder(pv.Vec3(x, 0, 8), 3.0, 12.0)
    post.set_attribute(pv.DefaultAttributes.COLOR_RGBA, pv.Vec4Attribute(0.1, 0.3, 0.9, 1.0))
    posts.append(post)

# The blend radius eases from 0 (sharp) at the left end to 2 mm at the right. ease() keeps the
# field in [0, 1], so the radius knows its range [0, 2] and needs no ScalarParameter.
radius = pv.FloatAttribute("x").normalize(-35.0, 35.0).ease("smoothstep") * 2.0
joint = pv.Union([plate] + posts, blend_radius=radius)

viz.Render(joint)
