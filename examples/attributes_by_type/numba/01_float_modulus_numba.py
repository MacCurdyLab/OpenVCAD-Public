import pyvcad as pv
import pyvcad_rendering as viz
from numba import cfunc, types

materials = pv.default_materials

length = 40.0
width = 10.0
height = 10.0
half_length = length / 2.0
modulus_min = 1.0
modulus_span = 9.0


@cfunc(types.float64(types.float64, types.float64, types.float64, types.float64))
def modulus_gradient(x, y, z, d):
    t = (x + half_length) / length
    if t < 0.0:
        t = 0.0
    elif t > 1.0:
        t = 1.0
    return modulus_min + modulus_span * t


bar = pv.RectPrism(pv.Vec3(0, 0, 0), pv.Vec3(length, width, height))
bar.set_attribute(pv.DefaultAttributes.MODULUS, pv.FloatAttribute(modulus_gradient))

root = bar
viz.Render(root, materials)
