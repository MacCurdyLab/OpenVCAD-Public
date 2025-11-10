import pyvcad as pv
import pyvcad_rendering as viz

materials = pv.default_materials
white = materials.id("white") # Soft
black = materials.id("black") # Hard
magenta = materials.id("magenta") # Hard
yellow = materials.id("yellow") # Hard

blank = pv.Mesh("../data/3d_models/keychain_blank.3mf", yellow)

# Apply mechanical properties to the blank (soft to hard)
graded_blank = pv.FGrade(["min(max((-x/80)+0.835,0.5),1)", "min(max((x/80)+0.165,0),0.5)"],
                                [white, black], True,
                                blank)

# Import text as mesh and scale and rotate it
text = pv.Scale(1,2,1, 
                pv.Rotate(0,0,180, pv.Vec3(0,0,0),
                          pv.Mesh("../data/3d_models/openvcad_text.stl", yellow)
                          )
                )

# Apply color grading to the text (magenta to yellow)
graded_text = pv.FGrade(["x/50+0.5", "-x/50+0.5"],
                        [magenta, yellow], True,
                        text)
scaled_text = pv.Scale(0.68,1.0,0.68, graded_text)

# Clip text to the blank bounds, this is because the text is taller
clipped_text = pv.Intersection(False, [scaled_text, blank])

# Combine the blank and the text to form the keychain
keychain = pv.Union(False, [clipped_text, graded_blank])

# Rotate the keychain to be upright (keychain is designed to be printed flat)
keychain = pv.Rotate(90,180,180, pv.Vec3(0,0,0), keychain)

root = keychain
viz.Render(root, materials)