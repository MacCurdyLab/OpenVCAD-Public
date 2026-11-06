import pyvcad as pv
import pyvcad_rendering as viz

materials = pv.default_materials
red = materials.id("red")
blue = materials.id("blue")

# Simplex noise with three octaves: smooth blobs with finer detail on top, in [-1, 1].
blobs = pv.FloatAttribute.noise("simplex", seed=4, frequency=0.06, octaves=3)

# Cellular F2 - F1 noise: 0 on the walls between random cells, so a low threshold traces a web.
cells = pv.FloatAttribute.noise("cellular_f2_minus_f1", seed=4, frequency=0.12)

# Left plate: the blobs mapped to a red fraction between 0 and 1.
left = pv.RectPrism(pv.Vec3(-27, 0, 0), pv.Vec3(50, 50, 4))
blob_red = blobs.map_range(-0.4, 0.4, 0.0, 1.0, clamp=True)
left.set_attribute(pv.DefaultAttributes.VOLUME_FRACTIONS,
                   pv.VolumeFractionsAttribute([(blob_red, red), (1.0 - blob_red, blue)]))

# Right plate: red walls where F2 - F1 is small, blue cell interiors, eased for a soft edge.
right = pv.RectPrism(pv.Vec3(27, 0, 0), pv.Vec3(50, 50, 4))
wall_blue = cells.normalize(0.0, 0.15).ease("smoothstep")
right.set_attribute(pv.DefaultAttributes.VOLUME_FRACTIONS,
                    pv.VolumeFractionsAttribute([(1.0 - wall_blue, red), (wall_blue, blue)]))

viz.Render(pv.Union(left, right), materials)
