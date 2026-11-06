import pyvcad as pv
import pyvcad_rendering as viz

# A square bar, 12 x 12 x 60 mm, standing on the plane z = 0, with a row of holes through it
bar = pv.RectPrism(pv.Vec3(0, 0, 30), pv.Vec3(12, 12, 60))
holes = pv.Union(0.0, [pv.Rotate(90, 0, 0, pv.Cylinder(pv.Vec3(0, 0, z), 2.5, 14.0)) for z in range(6, 60, 8)])
bar = pv.Difference(bar, holes)

# Twist about the z axis. The rate is in degrees per millimetre and may be a field: here it grows
# with height, so the bottom stays nearly straight and the top winds tighter. A field rate is read
# along the axis and integrated, so the angle at height z is 0.08 * z^2 / 2 degrees (144 at the top).
rate = pv.FloatAttribute("0.08 * z")
twisted = pv.Warp.twist(rate, bar, axis=pv.Vec3(0, 0, 1), origin=pv.Vec3(0, 0, 0))

# The twist angle is a coordinate field, so material can follow it: soft where straight, stiff where wound.
twisted.set_attribute(pv.DefaultAttributes.MODULUS,
                      twisted.coordinate_field("angle").map_range(0.0, 144.0, 100.0, 1000.0))

viz.Render(twisted)
