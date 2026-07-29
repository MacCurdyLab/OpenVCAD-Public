import pyvcad as pv
import pyvcad_rendering as viz

materials = pv.default_materials
red = materials.id("red")
blue = materials.id("blue")
clear = materials.id("clear")

body = pv.Mesh("../data/3d_models/utah_teapot_body.3mf")
lid = pv.Mesh("../data/3d_models/utah_teapot_lid.3mf")

# Grade body along z-axis
body_vfa = pv.VolumeFractionsAttribute([
    ("z/37-0.05", red),
    ("-z/37+1.05", blue),
])
body.set_attribute(pv.DefaultAttributes.VOLUME_FRACTIONS, body_vfa)

# Grade lid radially
lid_vfa = pv.VolumeFractionsAttribute([
    ("rho/15-0.45", red),
    ("-rho/15+1.45", clear),
])
lid.set_attribute(pv.DefaultAttributes.VOLUME_FRACTIONS, lid_vfa)

teapot = pv.Union(body, lid)

# Set material definitions on the root so the renderer can resolve colors
root_vfa = pv.VolumeFractionsAttribute()
teapot.set_attribute(pv.DefaultAttributes.VOLUME_FRACTIONS, root_vfa)

root = teapot
viz.Render(root, materials=materials)