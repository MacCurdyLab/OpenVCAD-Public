"""
Function Demo - Any implicit shape from a formula, as a string or a Python function.

Function evaluates a formula as the signed distance to a surface: negative
inside, positive outside. The formula can be a math expression string (via
exprtk) or a Python function. Expressions can use Cartesian (x, y, z),
cylindrical (rho, phic, z) and spherical (r, theta, phis) coordinates.

The min/max box is part of the shape: nothing outside it is solid. Make it a
little larger than the shape the formula describes.
"""
import pyvcad as pv
import pyvcad_rendering as viz
from numba import cfunc, types

# A six-petal flower outline, 6 mm thick: in cylindrical coordinates the
# outline radius swings between 7.5 and 12.5 mm around the Z axis, and
# max() intersects that prism with the slab |z| <= 3.
flower = pv.Function(
    "max(rho - (10 + 2.5 * cos(6 * phic)), abs(z) - 3)",
    pv.Vec3(-13.0, -13.0, -3.5),
    pv.Vec3(13.0, 13.0, 3.5),
)


# A rounded cube as a numba-compiled Python function (the fast path for
# callables): the 4-norm (x^4 + y^4 + z^4)^(1/4) gives a cube with soft edges.
@cfunc(types.float64(types.float64, types.float64, types.float64))
def rounded_cube_field(x, y, z):
    return (x ** 4 + y ** 4 + z ** 4) ** 0.25 - 8.0


rounded_cube = pv.Translate(
    30.0, 0.0, 0.0,
    pv.Function(rounded_cube_field, pv.Vec3(-9.0, -9.0, -9.0), pv.Vec3(9.0, 9.0, 9.0)),
)

root = pv.Union(flower, rounded_cube)

viz.Render(root)
