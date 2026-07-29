import pyvcad as pv
import pyvcad_rendering as viz

materials = pv.default_materials
red = materials.id("red")
blue = materials.id("blue")

mesh = pv.Mesh("../../data/3d_models/gear.stl")

# Grade material radially using sigmoid function
vfa = pv.VolumeFractionsAttribute([
    ("1 / (1 + exp(-4.5*(rho - 4)))", red),
    ("(-1 / (1 + exp(-4.5*(rho - 4)))) + 1", blue),
])
mesh.set_attribute(pv.DefaultAttributes.VOLUME_FRACTIONS, vfa)

root = mesh
viz.Render(root, materials=materials)