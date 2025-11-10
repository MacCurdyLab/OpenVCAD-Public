import pyvcad as pv
import pyvcad_rendering as viz

materials = pv.default_materials
red = materials.id("red")
blue = materials.id("blue")

text = pv.Rotate(0,0,180, pv.Vec3(0,0,0),
                    pv.Mesh("../data/3d_models/openvcad_text.stl", red)
                )

gradient = pv.FGrade(["0.12", "((1.0/3.5) * (z^2)) / 14.0"],
                      [red, blue], True, text)              
root = gradient

viz.Render(root, materials)