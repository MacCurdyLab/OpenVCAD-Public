import pyvcad as pv
import pyvcad_rendering as viz

materials = pv.default_materials
red = materials.id("red")
blue = materials.id("blue")

# Two reference bodies: a sphere on the left and a block on the right. They are not part of
# the design; they only define where the material grade starts and ends.
start = pv.Sphere(pv.Vec3(-30, 0, 0), 6.0)
end = pv.RectPrism(pv.Vec3(32, 0, 0), pv.Vec3(6, 24, 24))

# 0 on and inside the sphere, 1 on and inside the block, graded by the distances to both,
# so the contours bend around each body's shape. The bandwidth covers the gap between them.
blend = pv.FloatAttribute.between(start, end, bandwidth=60.0)

plate = pv.RectPrism(pv.Vec3(0, 0, 0), pv.Vec3(80, 40, 6))
plate.set_attribute(pv.DefaultAttributes.VOLUME_FRACTIONS,
                    pv.VolumeFractionsAttribute([(1.0 - blend, red), (blend, blue)]))

viz.Render(plate, materials)
