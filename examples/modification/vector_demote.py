"""
Demote Vec3 / Vec4 attributes into named float components.

COLOR_RGB and COLOR_RGBA gradients are split with Vec3ToScalarsConverter and
Vec4ToScalarsConverter. The demoted channels are then recombined with a channel
swap so the conversion is visible in the renderer.
"""
import pyvcad as pv
import pyvcad_rendering as viz

bar_length = 50.0
bar_width = 12.0
bar_height = 12.0
gap = 20.0

half_x = bar_length / 2.0
half_y = bar_width / 2.0
half_z = bar_height / 2.0

# --- Vec3 demote: COLOR_RGB -> red/green/blue floats, then swap channels ---
rgb_bar = pv.RectPrism(pv.Vec3(0, 0, 0), pv.Vec3(bar_length, bar_width, bar_height))
rgb_bar.set_attribute(
    pv.DefaultAttributes.COLOR_RGB,
    pv.Vec3Attribute(
        f"clamp((x + {half_x}) / {bar_length}, 0, 1)",
        f"clamp((y + {half_y}) / {bar_width}, 0, 1)",
        f"clamp((z + {half_z}) / {bar_height}, 0, 1)",
    ),
)
rgb_bar = pv.AttributeModifier(
    pv.Vec3ToScalarsConverter(
        pv.DefaultAttributes.COLOR_RGB,
        "red_channel",
        "green_channel",
        "blue_channel",
    ),
    rgb_bar,
)
# Rebuild COLOR_RGB as (G, B, R) to prove the demoted floats are usable.
rgb_bar = pv.AttributeModifier(
    pv.ScalarsToVec3Converter(
        "green_channel",
        "blue_channel",
        "red_channel",
        pv.DefaultAttributes.COLOR_RGB,
    ),
    rgb_bar,
)

# --- Vec4 demote: COLOR_RGBA -> r/g/b/a floats, then swap RGB and keep A ---
rgba_bar = pv.RectPrism(pv.Vec3(0, 0, 0), pv.Vec3(bar_length, bar_width, bar_height))
rgba_bar.set_attribute(
    pv.DefaultAttributes.COLOR_RGBA,
    pv.Vec4Attribute(
        f"clamp((x + {half_x}) / {bar_length}, 0, 1)",
        f"clamp((y + {half_y}) / {bar_width}, 0, 1)",
        f"clamp((z + {half_z}) / {bar_height}, 0, 1)",
        "1.0",
    ),
)
rgba_bar = pv.AttributeModifier(
    pv.Vec4ToScalarsConverter(
        pv.DefaultAttributes.COLOR_RGBA,
        "rgba_r",
        "rgba_g",
        "rgba_b",
        "rgba_a",
    ),
    rgba_bar,
)
rgba_bar = pv.AttributeModifier(
    pv.ScalarsToVec4Converter(
        "rgba_g",
        "rgba_b",
        "rgba_r",
        "rgba_a",
        pv.DefaultAttributes.COLOR_RGBA,
    ),
    rgba_bar,
)
# Also publish COLOR_RGB so both bars are visible under the default color view.
rgba_bar = pv.AttributeModifier(
    pv.ScalarsToVec3Converter(
        "rgba_g",
        "rgba_b",
        "rgba_r",
        pv.DefaultAttributes.COLOR_RGB,
    ),
    rgba_bar,
)

rgb_bar = pv.Translate(0.0, gap / 2.0, 0.0, rgb_bar)
rgba_bar = pv.Translate(0.0, -gap / 2.0, 0.0, rgba_bar)

root = pv.Union(rgb_bar, rgba_bar)

viz.Render(root)
