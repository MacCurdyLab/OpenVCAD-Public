import pyvcad as pv
import pyvcad_rendering as viz

# A cube whose colour grades from blue to red along x.
cube = pv.RectPrism(pv.Vec3(0, 0, 0), pv.Vec3(20, 20, 20))
cube.set_attribute(pv.DefaultAttributes.COLOR_RGBA,
                   pv.Vec4Attribute("0.5 + x / 20", "0.25", "0.5 - x / 20", "1"))

# The offset distance is a field: 0.5 mm at x = -10 rising to 4 mm at x = +10, clamped so the
# bounds hold everywhere. The bounds size the bounding box; the slope bound (3.5 mm over 20 mm)
# keeps the result a safe distance.
distance = pv.FloatAttribute("2.25 + 0.175 * x").clamp(0.5, 4.0)
parameter = pv.ScalarParameter(distance, minimum=0.5, maximum=4.0, lipschitz=0.175)

# GrowthPolicy.extend carries the cube's colour straight out into the grown material.
grown = pv.Offset(parameter, cube, growth=pv.GrowthPolicy.extend)

viz.Render(grown)
