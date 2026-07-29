import pyvcad as pv
import pyvcad_rendering as viz
from numba import cfunc, types

length = 50.0
width = 18.0
height = 8.0
half_length = length / 2.0
half_width = width / 2.0


@cfunc(types.float64(types.float64, types.float64, types.float64, types.float64))
def color_r(x, y, z, d):
    t = (x + half_length) / length
    if t < 0.0:
        t = 0.0
    elif t > 1.0:
        t = 1.0
    return t


@cfunc(types.float64(types.float64, types.float64, types.float64, types.float64))
def color_g(x, y, z, d):
    t = (y + half_width) / width
    if t < 0.0:
        t = 0.0
    elif t > 1.0:
        t = 1.0
    return 0.2 + 0.6 * t


@cfunc(types.float64(types.float64, types.float64, types.float64, types.float64))
def color_b(x, y, z, d):
    t = (x + half_length) / length
    if t < 0.0:
        t = 0.0
    elif t > 1.0:
        t = 1.0
    return 1.0 - t


@cfunc(types.float64(types.float64, types.float64, types.float64, types.float64))
def color_a(x, y, z, d):
    return 1.0


panel = pv.RectPrism(pv.Vec3(0, 0, 0), pv.Vec3(length, width, height))
panel.set_attribute(
    pv.DefaultAttributes.COLOR_RGBA,
    pv.Vec4Attribute(color_r, color_g, color_b, color_a),
)

root = panel
viz.Render(root)
