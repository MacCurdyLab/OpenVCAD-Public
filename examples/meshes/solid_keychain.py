import pyvcad as pv
import pyvcad_rendering as viz

materials = pv.default_materials
red = materials.id("red")
blue = materials.id("blue")
clear = materials.id("clear")

blank = pv.Mesh("../data/3d_models/keychain_blank.3mf", clear)

# Create text, fill with gyroid, and grade color
text = pv.Mesh("../data/3d_models/openvcad_text.stl", red)
gyroid = pv.Function("sin((0.75 * pi * x) / 1.0) * cos((0.75 * pi * y) / 1.0) + sin((0.75 * pi * y) / 1.0) * cos((0.75 * pi * z) / 1.0) + sin((0.75 * pi * z) / 1.0) * cos((0.75 * pi * x) / 1.0) + 0.9",
                     red, pv.Vec3(-25, -5.5, -1.5), pv.Vec3(35, 5.5, 1.5))
gyroid_fill = pv.Intersection(False, [text, gyroid])
graded_gyroid = pv.FGrade(["x/50+0.5", "-x/50+0.5"],
                          [red, blue], True,
                          gyroid_fill)
graded_gyroid = pv.Scale(0.68,0.68,0.68, graded_gyroid)

# Clip gyroid to the blank bounds
clipped_gyroid = pv.Intersection(False, [graded_gyroid, blank])

# Combine the blank and the gyroid to form the keychain
keychain = pv.Union(False, [clipped_gyroid, blank])

# Rotate the keychain to be upright (keychain is designed to be printed flat)
root = pv.Rotate(90,180,180, pv.Vec3(0,0,0), keychain)

viz.Render(root, materials)