import pyvcad as pv
import pyvcad_rendering as viz

# A finite linear array: five copies of a rounded peg along x, cells of 8 mm.
peg = pv.Offset(0.8, pv.RectPrism(pv.Vec3(0, 0, 0), pv.Vec3(4, 4, 10)))
row = pv.Tile(8.0, 8.0, 14.0, peg, count=(5, 1, 1))

# The copy index is a field: here each copy gets a stiffer modulus than the one before.
row.set_attribute(pv.DefaultAttributes.MODULUS, 100.0 + 50.0 * row.instance_index_field(0))

# A polar array: eight fan blades around the z axis, spread over a 270 degree arc, on a hub.
blade = pv.RectPrism(pv.Vec3(13, 0, 7), pv.Vec3(14, 2.5, 3))
fan = pv.PolarArray(8, blade, angle_range=(0.0, 270.0))
fan.set_attribute(pv.DefaultAttributes.MODULUS, 100.0 + 200.0 / 7.0 * fan.instance_index_field())
hub = pv.Cylinder(pv.Vec3(0, 0, 7), 6.0, 3.0)
hub.set_attribute(pv.DefaultAttributes.MODULUS, pv.FloatAttribute(100.0))

# Place the fan beside the row.
root = pv.Union(row, pv.Translate(72.0, 4.0, 0.0, pv.Union(fan, hub)))

viz.Render(root)
