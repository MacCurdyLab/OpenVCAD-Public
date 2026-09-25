"""
Map a scalar attribute into VOLUME_FRACTIONS with AttributeModifier.

A shore-hardness gradient along X is converted into a two-material blend
via VolumeFractionsExpressionConverter.
"""
import pyvcad as pv
import pyvcad_rendering as viz

materials = pv.default_materials

bar_length = 60.0
bar_width = 12.0
bar_height = 12.0

bar = pv.RectPrism(pv.Vec3(0, 0, 0), pv.Vec3(bar_length, bar_width, bar_height))

# Shore hardness ramps 0 -> 100 along X.
shore_expr = f"clamp((x + {bar_length / 2}) / {bar_length}, 0, 1) * 100.0"
bar.set_attribute(pv.DefaultAttributes.SHORE_HARDNESS, pv.FloatAttribute(shore_expr))

# Soft (blue) at low hardness, hard (red) at high hardness.
converter = pv.VolumeFractionsExpressionConverter(
    input_attributes=[pv.DefaultAttributes.SHORE_HARDNESS],
    materials=[materials.id("blue"), materials.id("red")],
    expressions=[
        f"1.0 - ({pv.DefaultAttributes.SHORE_HARDNESS} / 100.0)",
        f"{pv.DefaultAttributes.SHORE_HARDNESS} / 100.0",
    ],
)
root = pv.AttributeModifier(converter, bar)

viz.Render(root, materials)
