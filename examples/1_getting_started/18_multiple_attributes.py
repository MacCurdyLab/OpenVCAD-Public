import pyvcad as pv
import pyvcad_rendering as viz

materials = pv.default_materials
cube = pv.RectPrism(pv.Vec3(0, 0, 0), pv.Vec3(20, 20, 20))

# 1. Modulus Attribute (Linear increase along Z)
modulus = pv.FloatAttribute("z + 10")
cube.set_attribute(pv.DefaultAttributes.MODULUS, modulus)

# 2. Color Attribute (Green to Magenta gradient along X)
color = pv.Vec4Attribute(
    "x/20 + 0.5",
    "1.0 - (x/20 + 0.5)",
    "x/20 + 0.5",
    "1.0"
)
cube.set_attribute(pv.DefaultAttributes.COLOR_RGBA, color)

# 3. Volume Fractions Attribute (Mixes Gray and Green materials along Y)
fractions = pv.VolumeFractionsAttribute(
    [
        ("-y/20 + 0.5", materials.id("gray")),
        ("y/20 + 0.5", materials.id("green"))
    ]
)
cube.set_attribute(pv.DefaultAttributes.VOLUME_FRACTIONS, fractions)

# You can select which attribute to visualize using the dropdown
# in the top right corner of the render window!
root = cube
viz.Render(root, materials)
