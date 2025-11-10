import pyvcad as pv
import pyvcad_rendering as viz

materials = pv.default_materials

# Define a cylinder we will use multiple times
# Syntax: pv.Cylinder(center point, radius, height, material id)
base_cylinder = pv.Cylinder(pv.Vec3(0,0,0), 2, 9, materials.id("gray"))

root = pv.Difference(
    pv.Intersection(False, [
        pv.RectPrism(pv.Vec3(0,0,0), pv.Vec3(8,8,8), materials.id("gray")),
        pv.Sphere(pv.Vec3(0,0,0), 5.5, materials.id("gray"))
    ]),
    pv.Union(False, [
        base_cylinder,
        #  Syntax: pv.Rotate(pitch,yaw,roll, around point, child node)
        pv.Rotate(90,0,0, pv.Vec3(0,0,0), base_cylinder), 
        pv.Rotate(0,90,0, pv.Vec3(0,0,0), base_cylinder)
    ])
)

viz.Render(root, materials)