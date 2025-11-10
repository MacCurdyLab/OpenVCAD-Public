import pyvcad as pv
import pyvcad_rendering as viz

materials = pv.default_materials
red = materials.id("red")
blue = materials.id("blue")
clear = materials.id("clear")

body = pv.Mesh("../data/3d_models/utah_teapot_body.3mf", red)
lid = pv.Mesh("../data/3d_models/utah_teapot_lid.3mf", blue)

graded_body = pv.FGrade(["z/37-0.05", "-z/37+1.05"],
                        [red, blue], True, body)

graded_lid = pv.FGrade(["rho/15-0.45", "-rho/15+1.45"],
                       [red, clear], True, lid)

teapot = pv.Union(False, [graded_body, graded_lid])
root = teapot

viz.Render(root, materials)