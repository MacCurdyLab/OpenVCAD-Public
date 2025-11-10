import pyvcad as pv
import pyvcad_rendering as viz

materials = pv.default_materials

bar = pv.RectPrism(pv.Vec3(0,0,0), pv.Vec3(25, 25, 5), materials.id("gray"))

# A functional gradient that is radial in cylindrical coordinates
root = pv.FGrade(["rho/10", "1 - (rho/10)"], [materials.id("red"), materials.id("blue")], False)
root.set_child(bar)

viz.Render(root, materials)