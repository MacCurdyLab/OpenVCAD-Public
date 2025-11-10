# This example shows how you can use the 'd' variable with the fgrade node. 
# 'd' is the signed distance to the surface: negative values are inside 
import pyvcad as pv
import pyvcad_rendering as viz

materials = pv.default_materials

# Create two overlapping spheres
radius = 5
left_sphere  = pv.Sphere(pv.Vec3(-radius/2, 0, 0), radius, materials.id("red"))
right_sphere = pv.Sphere(pv.Vec3(+radius/2, 0, 0), radius, materials.id("red"))

# Perform boolean operation
uni = pv.Union()
uni.add_child(left_sphere)
uni.add_child(right_sphere)

# Create a gradient that is blue at the surface and changes to red
fgrade = pv.FGrade(["abs(d)/3","-abs(d)/3 + 1"], [materials.id("red"),materials.id("blue")], True, uni)

# This is used to just take a section through the object so we can see the gradient
cutter = pv.RectPrism(pv.Vec3(0,-2.5,0), pv.Vec3(20,5,11), 1)
intersection = pv.Intersection(False, [fgrade, cutter])

root = intersection

viz.Render(root, materials)
