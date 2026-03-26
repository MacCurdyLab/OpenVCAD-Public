import pyvcad as pv

materials = pv.default_materials()
red = materials.id("red")
blue = materials.id("blue")

lattice_mesh = pv.Mesh(pv.resources_path() + "examples/data/3d_models/plate_lattice.stl", red)
fgrade = pv.FGrade(["min(max((-z/180)+0.88,0.75),1)",
                    "min(max((z/180)+0.12,0),0.25)"], [red, blue], False)
fgrade.set_child(lattice_mesh)
root = fgrade