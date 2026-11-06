import pyvcad as pv
import pyvcad_rendering as viz

materials = pv.default_materials
red = materials.id("red")
blue = materials.id("blue")

# A square bar standing on the plane z = 0, graded red to blue up its height.
bar = pv.RectPrism(pv.Vec3(0, 0, 30), pv.Vec3(12, 12, 60))
bar.set_attribute(pv.DefaultAttributes.VOLUME_FRACTIONS, pv.VolumeFractionsAttribute([
    ("z / 60", red),
    ("1 - z / 60", blue),
]))

# The twist rate, in degrees per mm, follows a smooth transfer curve of height: no twist in the
# bottom third, a smooth rise, then a steady 9 degrees per mm in the top third.
rate = pv.FloatAttribute("z").transfer([(0.0, 0.0), (20.0, 0.0), (40.0, 9.0), (60.0, 9.0)], interpolation="smooth")
twisted = pv.Warp.twist(rate, bar)

viz.Render(twisted, materials)
