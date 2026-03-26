import pyvcad as pv

materials = pv.default_materials()
red = materials.id("red")
blue = materials.id("blue")

fgrade = pv.FGrade(["1 / (1 + exp(-4.5(rho - 4)))", 
                    "(-1 / (1 + exp(-4.5(rho - 4)))) + 1"],
                   [red, blue], True)
fgrade.set_child(
    pv.Mesh(pv.resources_path() + "examples/data/3d_models/gear.stl", red)
)
root = fgrade