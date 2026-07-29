import pyvcad as pv
import pyvcad_rendering as viz
from numba import cfunc, types

materials = pv.default_materials

length = 50.0
width = 18.0
height = 8.0
half_length = length / 2.0


@cfunc(types.float64(types.float64, types.float64, types.float64, types.float64))
def blue_fraction(x, y, z, d):
    t = (x + half_length) / length
    if t < 0.0:
        t = 0.0
    elif t > 1.0:
        t = 1.0
    return t


@cfunc(types.float64(types.float64, types.float64, types.float64, types.float64))
def green_fraction(x, y, z, d):
    t = (x + half_length) / length
    if t < 0.0:
        t = 0.0
    elif t > 1.0:
        t = 1.0
    return 1.0 - t


panel = pv.RectPrism(pv.Vec3(0, 0, 0), pv.Vec3(length, width, height))
panel.set_attribute(
    pv.DefaultAttributes.VOLUME_FRACTIONS,
    pv.VolumeFractionsAttribute(
        [
            (blue_fraction, materials.id("blue")),
            (green_fraction, materials.id("green")),
        ]
    ),
)

root = panel
viz.Render(root, materials)
