import pyvcad as pv
import pyvcad_rendering as viz

materials = pv.default_materials
yellow = materials.id("yellow")
magenta = materials.id("magenta")
clear = materials.id("clear")
black = materials.id("black")

# Build the QR code
qr_code_base = pv.Mesh("../data/3d_models/qr_code_base.3mf", yellow, True)
qr_code = pv.Mesh("../data/3d_models/qr_code_code.3mf", black, True)
qr_code_boarder = pv.Mesh("../data/3d_models/qr_code_border.3mf", black, True)
qr_code_combined = pv.Union(False, [qr_code_base, qr_code, qr_code_boarder])
qr_code_combined = pv.Translate(-69,0,-1.5, qr_code_combined)

# Create text, fill with gyroid, and apply gradient
openvcad_text = pv.Rotate(0,0,180, pv.Vec3(0,0,0), pv.Mesh("../data/3d_models/openvcad_text.stl", yellow))
gyroid = pv.Function("sin((1.1 * pi * x) / 1.0) * cos((1.1 * pi * y) / 1.0) + sin((1.1 * pi * y) / 1.0) * cos((1.1 * pi * z) / 1.0) + sin((1.1 * pi * z) / 1.0) * cos((1.1 * pi * x) / 1.0) + 0.5",
                     yellow, pv.Vec3(-72, -18, -6), pv.Vec3(72, 18, 6))
gyroid_fill = pv.Intersection(False, [openvcad_text, gyroid])
text_gradient = pv.FGrade(["x/68+0.5", "-x/68+0.5"],[magenta, yellow], True, gyroid_fill)

# Scale and position the text
text_gradient = pv.Rotate(90,180,180, pv.Vec3(0,0,0), pv.Translate(15,0,0, pv.Scale(2,2,2, text_gradient)))

# Create a clear bar to hold the QR code and text
bar = pv.RectPrism(pv.Vec3(0,0,0), pv.Vec3(173, 32, 12), clear)

root = pv.Union(False, [qr_code_combined, text_gradient, bar])

viz.Render(root, materials)