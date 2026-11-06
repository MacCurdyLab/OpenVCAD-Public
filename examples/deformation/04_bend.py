import pyvcad as pv
import pyvcad_rendering as viz

materials = pv.default_materials

# A straight strip along x, 94 mm long, 12 mm wide and 3 mm thick, lying on the plane z = 0, with slots
strip = pv.RectPrism(pv.Vec3(0, 0, -1.5), pv.Vec3(94, 12, 3))
slots = pv.Union(0.0, [pv.RectPrism(pv.Vec3(x, 0, -1.5), pv.Vec3(2, 8, 4)) for x in range(-42, 43, 6)])
strip = pv.Difference(strip, slots)
strip.set_attribute(pv.DefaultAttributes.VOLUME_FRACTIONS, pv.VolumeFractionsAttribute([
    ("(x + 47) / 94", materials.id("red")),
    ("1 - (x + 47) / 94", materials.id("blue")),
]))

# Bend the line along +x (through the origin) around an axis along +y with a 15 mm radius. A positive
# radius bends toward direction x axis = +z, so the strip curls up into a near circle (94 mm is just
# under the 2 pi 15 = 94.2 mm circumference). Lengths on the plane z = 0 are kept.
bent = pv.Warp.bend(15.0, strip, origin=pv.Vec3(0, 0, 0), direction=pv.Vec3(1, 0, 0), axis=pv.Vec3(0, 1, 0))

viz.Render(bent, materials)
