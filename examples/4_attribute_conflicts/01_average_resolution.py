import pyvcad as pv
import pyvcad_rendering as viz

materials = pv.default_materials

left_sphere = pv.Sphere(pv.Vec3(-4, 0, 0), 10.0)
right_sphere = pv.Sphere(pv.Vec3(4, 0, 0), 10.0)

# Red 
left_sphere.set_attribute(pv.DefaultAttributes.COLOR_RGBA, pv.Vec4Attribute("1.0", "0.0", "0.0", "1.0"))
# Blue
right_sphere.set_attribute(pv.DefaultAttributes.COLOR_RGBA, pv.Vec4Attribute("0.0", "0.0", "1.0", "1.0"))

root = pv.Intersection(left_sphere, right_sphere)

# Instead of the default behavior, we average them.
# The entire resulting intersection lens will be purple instead or red or blue!
root.set_attribute_conflict_resolver(pv.DefaultAttributes.COLOR_RGBA, pv.resolvers.AverageConflictResolver())

viz.Render(root, materials)
