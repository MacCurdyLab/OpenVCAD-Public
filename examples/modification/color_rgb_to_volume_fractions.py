"""
Demote COLOR_RGB into scalar channels, then map the red channel to volume fractions.

COLOR_RGB is split with Vec3ToScalarsConverter. Only the demoted red channel is
used: a simple threshold chooses between two materials.
"""
import pyvcad as pv
import pyvcad_rendering as viz

materials = pv.default_materials

bar_length = 60.0
bar_width = 12.0
bar_height = 12.0
half_x = bar_length / 2.0

# Same spatial ramp on R, G, and B.
channel_expr = f"clamp((x + {half_x}) / {bar_length}, 0, 1)"

bar = pv.RectPrism(pv.Vec3(0, 0, 0), pv.Vec3(bar_length, bar_width, bar_height))
bar.set_attribute(
    pv.DefaultAttributes.COLOR_RGB,
    pv.Vec3Attribute(channel_expr, channel_expr, channel_expr),
)

# Split COLOR_RGB into named float attributes.
bar = pv.AttributeModifier(
    pv.Vec3ToScalarsConverter(
        pv.DefaultAttributes.COLOR_RGB,
        "red_channel",
        "green_channel",
        "blue_channel",
    ),
    bar,
)

# Threshold the demoted red channel into a hard two-material blend.
# red < 0.5 -> blue material, red >= 0.5 -> red material.
root = pv.AttributeModifier(
    pv.VolumeFractionsExpressionConverter(
        input_attributes=["red_channel"],
        materials=[materials.id("blue"), materials.id("red")],
        expressions=[
            "if(red_channel < 0.5, 1.0, 0.0)",
            "if(red_channel < 0.5, 0.0, 1.0)",
        ],
    ),
    bar,
)

viz.Render(root, materials)
