import pyvcad as pv
import pyvcad_rendering as viz

materials = pv.default_materials

bar = pv.RectPrism(pv.Vec3(0,0,0), pv.Vec3(100,50,10), materials.id("gray"))

# A functional gradient that is 100% blue at x=-50 and 100% at x=50
root = pv.FGrade(["x/100 + 0.5", "-x/100 + 0.5"],
                 [materials.id("red"), materials.id("blue")], False)
root.set_child(bar)

viz.Render(root, materials) # Render as usual

# UNCOMMENT THIS to export the object for 3D printing, simulation, etc.
# This brings up a wizard to guide you through the export process
viz.Export(root, materials)