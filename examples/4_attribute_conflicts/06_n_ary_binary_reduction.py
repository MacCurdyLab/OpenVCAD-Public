import pyvcad as pv
import pyvcad_rendering as viz
from numba import cfunc, types

materials = pv.default_materials

# 1. Define four rectangular prisms, one in each quadrant of the XY plane.
#    Each prism is 12x12x6 but offset so they overlap by 2 units along
#    each shared edge, creating a cross-shaped overlap region in the center.
q1 = pv.RectPrism(pv.Vec3( 5.0,  5.0, 0.0), pv.Vec3(12.0, 12.0, 6.0))
q2 = pv.RectPrism(pv.Vec3(-5.0,  5.0, 0.0), pv.Vec3(12.0, 12.0, 6.0))
q3 = pv.RectPrism(pv.Vec3(-5.0, -5.0, 0.0), pv.Vec3(12.0, 12.0, 6.0))
q4 = pv.RectPrism(pv.Vec3( 5.0, -5.0, 0.0), pv.Vec3(12.0, 12.0, 6.0))

# 2. Assign identical density scalars to each prism
q1.set_attribute("density", pv.FloatAttribute("1.0"))
q2.set_attribute("density", pv.FloatAttribute("1.0"))
q3.set_attribute("density", pv.FloatAttribute("1.0"))
q4.set_attribute("density", pv.FloatAttribute("1.0"))

# 3. Use BBoxUnion - an N-ary union node.
#    Conflicts in overlapping regions are resolved via Binary Reduction.
root = pv.BBoxUnion([q1, q2, q3, q4])

# 4. Define an additive custom resolver using a Numba cfunc.
#    The same binary function signature (left_val, right_val) is reused
#    for every pair during the reduction across all overlapping children.
@cfunc(types.float64(types.float64, types.float64))
def additive_density(left_val, right_val):
    return left_val + right_val

root.set_attribute_conflict_resolver(
    "density",
    pv.resolvers.CustomFloatConflictResolver(additive_density)
)

viz.Render(root, materials)
