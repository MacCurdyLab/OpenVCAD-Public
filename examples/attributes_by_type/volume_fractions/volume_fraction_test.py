import pyvcad as pv
import pyvcad_rendering as viz

materials = pv.default_materials
volume_fraction_map = [
    ('x/100+0.5', materials.id("red")),
    ('-x/100+0.5', materials.id("blue")),
]
vfa = pv.VolumeFractionsAttribute(volume_fraction_map)

rect_prism = pv.RectPrism(pv.Vec3(0,0,0), pv.Vec3(100,30,10))
rect_prism.set_attribute(pv.DefaultAttributes.VOLUME_FRACTIONS,vfa)

root = rect_prism
viz.Render(root, materials=materials)
