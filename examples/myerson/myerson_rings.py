import pyvcad as pv
import pyvcad_rendering as viz

materials = pv.default_materials
red = materials.id("red")
blue = materials.id("blue")

a = pv.Mesh("a.3mf", red)
grade_a = pv.FGrade(["0.75", "0.25"],[red, blue], True, a)
b = pv.Mesh("b.3mf", blue)
grade_b = pv.FGrade(["0.25", "0.75"],[red, blue], True, b)

root = pv.Union(False, [grade_a,grade_b])

viz.Render(root, materials)
viz.Export(root, materials)
