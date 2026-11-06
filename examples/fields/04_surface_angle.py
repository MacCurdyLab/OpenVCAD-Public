import pyvcad as pv
import pyvcad_rendering as viz

materials = pv.default_materials
red = materials.id("red")
blue = materials.id("blue")

part = pv.Sphere(pv.Vec3(0, 0, 0), 20.0)

# The angle between the surface normal and the build direction (+Z): 0 on skin facing up,
# 90 on vertical walls, 180 on overhangs facing the build plate. Inside the part each point
# takes the angle of its closest surface point.
angle = pv.FloatAttribute.surface_angle(part, direction=(0, 0, 1))

# Overhangs steeper than 45 degrees from vertical (angle above 135) get the red material,
# with a smooth band between 110 and 150 degrees.
overhang = angle.normalize(110.0, 150.0).ease("smoothstep")
part.set_attribute(pv.DefaultAttributes.VOLUME_FRACTIONS,
                   pv.VolumeFractionsAttribute([(overhang, red), (1.0 - overhang, blue)]))

viz.Render(part, materials)
