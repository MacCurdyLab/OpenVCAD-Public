import pyvcad as pv
import pyvcad_rendering as viz

materials = pv.default_materials

# A flat plate, 80 x 80 x 3 mm, with a grid of slots
plate = pv.RectPrism(pv.Vec3(0, 0, 1.5), pv.Vec3(80, 80, 3))
slots = pv.Union(0.0, [pv.RectPrism(pv.Vec3(x, y, 1.5), pv.Vec3(3, 10, 4))
                       for x in range(-32, 33, 8) for y in (-24, -8, 8, 24)])
plate = pv.Difference(plate, slots)
plate.set_attribute(pv.DefaultAttributes.VOLUME_FRACTIONS, pv.VolumeFractionsAttribute([
    ("(y + 40) / 80", materials.id("red")),
    ("1 - (y + 40) / 80", materials.id("blue")),
]))

# The displacement says where material goes: the material at X moves to X + u(X). Here a smooth bump
# pushes the middle of the plate up by 12 mm. u is read at the undeformed point, as a simulation
# result would be, so the slots stretch over the dome and the colours move with the material.
bump = ("0", "0", "12 * exp(-(x^2 + y^2) / 400)")
domed = pv.Warp.displace(bump, plate)

viz.Render(domed, materials)
