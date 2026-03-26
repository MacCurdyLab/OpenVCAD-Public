import pyvcad as pv

materials = pv.default_materials()
red = materials.id("red")
blue = materials.id("blue")

fgrade = pv.FGrade(["z/35", "-z/35+1"],[red, blue], True)
fgrade.set_child(
    pv.Mesh(pv.resources_path() + "examples/data/3d_models/3DBenchy.stl", red)
)
root = fgrade