import pyvcad as pv
import pyvcad_rendering as viz

materials = pv.default_materials
cyan = materials.id("cyan")
magenta = materials.id("magenta")
yellow = materials.id("yellow")

mesh = pv.Mesh("../data/3d_models/big_screwdriver.stl")

# Apply mechanical properties grading via volume fractions
vfa = pv.VolumeFractionsAttribute([
    ("y<=12", cyan),
    ("(y>12) ? (1 / (1 + exp(-0.175*(y - 35)))) : 0", magenta),
    ("(y>12) ? (-1 / (1 + exp(-0.175*(y - 35)))) + 1 : 0", yellow),
])
mesh.set_attribute(pv.DefaultAttributes.VOLUME_FRACTIONS, vfa)

root = mesh
viz.Render(root, materials=materials)