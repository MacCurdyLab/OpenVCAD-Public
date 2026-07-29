import pyvcad as pv
import pyvcad_rendering as viz
from numba import cfunc, types

materials = pv.default_materials

left_sphere = pv.Sphere(pv.Vec3(-4.0, 0, 0), 10.0)
right_sphere = pv.Sphere(pv.Vec3(4.0, 0, 0), 10.0)

# Left sphere has density 2.0
left_sphere.set_attribute("density", pv.FloatAttribute("2.0"))
# Right sphere has density 3.0
right_sphere.set_attribute("density", pv.FloatAttribute("3.0"))

root = pv.Intersection(left_sphere, right_sphere)

# We define a custom Numba C-callback for fast, compiled evaluation
# during the geometry sampling loop. Let's multiply the densities.
@cfunc(types.float64(types.float64, types.float64))
def multiply_densities(a, b):
    return a * b

# Apply the custom float resolver
root.set_attribute_conflict_resolver("density", pv.resolvers.CustomFloatConflictResolver(multiply_densities))

viz.Render(root, materials)
