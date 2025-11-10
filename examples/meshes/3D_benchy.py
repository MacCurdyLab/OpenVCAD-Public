import pyvcad as pv
import pyvcad_rendering as viz

materials = pv.default_materials
red = materials.id("red")
blue = materials.id("blue")

fgrade = pv.FGrade(["z/35", "-z/35+1"],[red, blue], True)
fgrade.set_child(
    pv.Mesh("../data/3d_models/3DBenchy.stl", red)
)
root = fgrade

viz.Render(root, materials)