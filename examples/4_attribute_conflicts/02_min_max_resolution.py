import pyvcad as pv
import pyvcad_rendering as viz

materials = pv.default_materials

# Two intersecting rectangular prisms forming a cross (+)
cube_x = pv.RectPrism(pv.Vec3(0, 0, 0), pv.Vec3(20, 6, 6))
cube_y = pv.RectPrism(pv.Vec3(0, 0, 0), pv.Vec3(6, 20, 6))

# Horizontal prism is Cyan (R=0, G=1, B=1)
cube_x.set_attribute(pv.DefaultAttributes.COLOR_RGBA, pv.Vec4Attribute("0.0", "1.0", "1.0", "1.0"))
# Vertical prism is Yellow (R=1, G=1, B=0)
cube_y.set_attribute(pv.DefaultAttributes.COLOR_RGBA, pv.Vec4Attribute("1.0", "1.0", "0.0", "1.0"))

root = pv.Union(cube_x, cube_y)

# We use MaxConflictResolver with PerChannel mode.
# The intersection takes the maximum of each color channel:
# Max(R=0, R=1) -> R=1
# Max(G=1, G=1) -> G=1
# Max(B=1, B=0) -> B=1
# The result in the center will be White (1, 1, 1).
resolver = pv.resolvers.MaxConflictResolver(pv.resolvers.Vec4Mode.PerChannel)
root.set_attribute_conflict_resolver(pv.DefaultAttributes.COLOR_RGBA, resolver)

viz.Render(root, materials)
