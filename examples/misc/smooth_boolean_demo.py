"""
Smooth Boolean Demo - Visualize the effect of smooth union on two spheres.

This example creates two overlapping spheres and applies a smooth union
with a visible smoothing radius, producing rounded transitions.
"""
import pyvcad as pv
import pyvcad_rendering as viz

materials = pv.default_materials

# Create two overlapping spheres
radius = 5
left_sphere  = pv.Sphere(pv.Vec3(-radius/2, 0, 0), radius, materials.id("red"))
right_sphere = pv.Sphere(pv.Vec3(+radius/2, 0, 0), radius, materials.id("blue"))

# Smooth union with k=2.0 for a pronounced blend
k = 2.0
root = pv.Union(k, False, [left_sphere, right_sphere])

viz.Render(root, materials)
