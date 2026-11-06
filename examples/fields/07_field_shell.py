import pyvcad as pv
import pyvcad_rendering as viz

materials = pv.default_materials
red = materials.id("red")
blue = materials.id("blue")

dome = pv.Sphere(pv.Vec3(0, 0, 0), 20.0)

# One field drives both the wall thickness and the material: how far the surface faces down.
# 0 on skin facing up, 1 on overhangs facing the build plate.
overhang = pv.FloatAttribute.surface_angle(dome, direction=(0, 0, 1)).normalize(60.0, 180.0).ease("smoothstep")

# An inward shell 1 mm thick on top, thickening to 4 mm under the overhang. The field knows its
# range (1 to 4 mm), so the shell needs no extra hints.
wall = pv.Shell(1.0 + 3.0 * overhang, dome)
wall.set_attribute(pv.DefaultAttributes.VOLUME_FRACTIONS,
                   pv.VolumeFractionsAttribute([(overhang, red), (1.0 - overhang, blue)]))

# Cut away the front half to show the wall.
section = pv.Difference(wall, pv.RectPrism(pv.Vec3(0, -15, 0), pv.Vec3(50, 30, 50)))

viz.Render(section, materials)
