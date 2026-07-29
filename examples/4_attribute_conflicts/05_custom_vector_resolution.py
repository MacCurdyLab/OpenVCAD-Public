import pyvcad as pv
import pyvcad_rendering as viz
from numba import cfunc, types

materials = pv.default_materials

cube_x = pv.RectPrism(pv.Vec3(0, 0, 0), pv.Vec3(20, 6, 6))
cube_y = pv.RectPrism(pv.Vec3(0, 0, 0), pv.Vec3(6, 20, 6))

# Horizontal prism is mostly Cyan
cube_x.set_attribute(pv.DefaultAttributes.COLOR_RGBA, pv.Vec4Attribute("0.2", "0.8", "0.8", "1.0"))
# Vertical prism is mostly Yellow
cube_y.set_attribute(pv.DefaultAttributes.COLOR_RGBA, pv.Vec4Attribute("0.8", "0.8", "0.2", "1.0"))

root = pv.Union(cube_x, cube_y)

# With CustomVec4ConflictResolver, we can configure completely different 
# logic for Red, Green, Blue, and Alpha channels in the overlap region.

@cfunc(types.float64(types.float64, types.float64))
def logic_r(a, b):
    return max(a, b) # Take maximum Red

@cfunc(types.float64(types.float64, types.float64))
def logic_g(a, b):
    return min(a, b) # Take minimum Green

@cfunc(types.float64(types.float64, types.float64))
def logic_b(a, b):
    return a + b     # Add Blue components

@cfunc(types.float64(types.float64, types.float64))
def logic_a(a, b):
    return 1.0       # Always solid alpha

resolver = pv.resolvers.CustomVec4ConflictResolver(logic_r, logic_g, logic_b, logic_a)
root.set_attribute_conflict_resolver(pv.DefaultAttributes.COLOR_RGBA, resolver)

viz.Render(root, materials)
