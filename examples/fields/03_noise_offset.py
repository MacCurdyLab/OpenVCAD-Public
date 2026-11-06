import pyvcad as pv
import pyvcad_rendering as viz

materials = pv.default_materials
red = materials.id("red")
blue = materials.id("blue")

# One field, used twice: fractal simplex noise mapped to [0, 1]. Noise seldom reaches -1 or 1,
# so map the middle of its range and clamp for strong contrast.
noise = pv.FloatAttribute.noise("simplex", seed=2, frequency=0.08, octaves=4)
bumps = noise.map_range(-0.5, 0.5, 0.0, 1.0, clamp=True)

# The field grades the material of a sphere...
sphere = pv.Sphere(pv.Vec3(0, 0, 0), 20.0)
sphere.set_attribute(pv.DefaultAttributes.VOLUME_FRACTIONS,
                     pv.VolumeFractionsAttribute([(bumps, red), (1.0 - bumps, blue)]))

# ...and drives its geometry: an offset of 0 to 3 mm. The noise knows its range and slope, so the
# offset needs no ScalarParameter hints, and GrowthPolicy.extend carries the colour outward.
rough = pv.Offset(bumps * 3.0, sphere, growth=pv.GrowthPolicy.extend)

viz.Render(rough, materials)
