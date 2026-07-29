import pyvcad as pv
import pyvcad_rendering as viz

materials = pv.default_materials
cube = pv.RectPrism(pv.Vec3(0, 0, 0), pv.Vec3(50, 10, 10))

# The volume fractions attribute defines mixing ratios of materials
# throughout the object's interior. Note that at any given point
# in space, the sum of all fractions must cleanly equal 1.0!
# We define a fraction expression mapping to the specific material ID.
fraction_gradient = pv.VolumeFractionsAttribute(
    [
        ("x/50 + 0.5", materials.id("blue")),
        ("-x/50 + 0.5", materials.id("red"))
    ]
)

# And attach it like any other attribute
cube.set_attribute(pv.DefaultAttributes.VOLUME_FRACTIONS, fraction_gradient)

# When using volume fractions, it's very important to supply
# the materials mapping so the renderer knows how to display the mix
root = cube
viz.Render(root, materials)
