import math

import pyvcad as pv
import pyvcad_rendering as viz

materials = pv.default_materials

# A flat perforated plate, 60 x 40 x 4 mm, centred on the origin
plate = pv.RectPrism(pv.Vec3(0, 0, 0), pv.Vec3(60, 40, 4))
holes = pv.Union(0.0, [pv.Cylinder(pv.Vec3(x, y, 0), 3.0, 6.0) for x in (-24, -12, 0, 12, 24) for y in (-12, 0, 12)])
part = pv.Difference(plate, holes)

# Material graded along the flat plate. It rides along with the warp, because the warp samples the
# plate (geometry and attributes) at the point each world point pulls back to.
part.set_attribute(pv.DefaultAttributes.VOLUME_FRACTIONS, pv.VolumeFractionsAttribute([
    ("(x + 30) / 60", materials.id("red")),
    ("1 - (x + 30) / 60", materials.id("blue")),
]))


# The map g takes a world point to the flat plate's point: here the plate rises and falls in a wave.
# A plain Python function returning three numbers is compiled with numba and runs without the GIL.
def ripple(x, y, z, d):
    return (x, y, z - 6.0 * math.sin(x / 10.0) * math.cos(y / 20.0))


# A warp moves material, so it needs the world box of the result: the wave adds 6 mm above and below.
warped = pv.Warp(ripple, part, bounds=(pv.Vec3(-30, -20, -9), pv.Vec3(30, 20, 9)))

viz.Render(warped, materials)
