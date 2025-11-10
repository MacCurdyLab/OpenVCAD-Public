import pyvcad as pv
import pyvcad_rendering as viz

materials = pv.default_materials
red = materials.id("red")
blue = materials.id("blue")

text = pv.Rotate(0,0,180, pv.Vec3(0,0,0),
                    pv.Mesh("../data/3d_models/openvcad_text.stl", red)
                )

gyroid = pv.Function("sin((2 * pi * x) / 1.0) * cos((2 * pi * y) / 1.0) + sin((2 * pi * y) / 1.0) * cos((2 * pi * z) / 1.0) + sin((2 * pi * z) / 1.0) * cos((2 * pi * x) / 1.0)", 
                     red, pv.Vec3(-35, -1.75, -7), pv.Vec3(35, 1.75, 7))

gyroid_fill = pv.Intersection(False, [text, gyroid])

gradient = pv.FGrade(["0.12", "((1.0/3.5) * (z^2)) / 14.0"],
                      [red, blue], True, gyroid_fill)              
root = gradient

viz.Render(root, materials)