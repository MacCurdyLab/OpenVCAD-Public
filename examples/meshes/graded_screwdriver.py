import pyvcad as pv
import pyvcad_rendering as viz

materials = pv.default_materials
cyan = materials.id("cyan")
magenta = materials.id("magenta")
yellow = materials.id("yellow")

fgrade = pv.FGrade(["y<=12", "(y>12) ? (1 / (1 + exp(-0.175(y - 35)))) : 0", 
                          "(y>12) ? (-1 / (1 + exp(-0.175(y - 35)))) + 1 : 0"],
                          [cyan, magenta, yellow], True)
fgrade.set_child(
    pv.Mesh("../data/3d_models/big_screwdriver.stl", cyan)
)
root = fgrade
viz.Render(root, materials)