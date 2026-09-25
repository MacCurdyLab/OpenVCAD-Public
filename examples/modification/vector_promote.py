"""
Promote named float attributes into Vec3 / Vec4 attributes.

Three independent float gradients become COLOR_RGB via ScalarsToVec3Converter.
Four float gradients become COLOR_RGBA via ScalarsToVec4Converter.
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

r_expr = f"clamp((x + {half_x}) / {bar_length}, 0, 1)"
g_expr = f"clamp((y + {half_y}) / {bar_width}, 0, 1)"
b_expr = f"clamp((z + {half_z}) / {bar_height}, 0, 1)"

# --- Promote three floats into COLOR_RGB ---
rgb_bar = pv.RectPrism(pv.Vec3(0, 0, 0), pv.Vec3(bar_length, bar_width, bar_height))
rgb_bar.set_attribute("red_channel", pv.FloatAttribute(r_expr))
rgb_bar.set_attribute("green_channel", pv.FloatAttribute(g_expr))
rgb_bar.set_attribute("blue_channel", pv.FloatAttribute(b_expr))
rgb_bar = pv.AttributeModifier(
    pv.ScalarsToVec3Converter(
        "red_channel",
        "green_channel",
        "blue_channel",
        pv.DefaultAttributes.COLOR_RGB,
    ),
    rgb_bar,
)

# --- Promote four floats into COLOR_RGBA ---
rgba_bar = pv.RectPrism(pv.Vec3(0, 0, 0), pv.Vec3(bar_length, bar_width, bar_height))
rgba_bar.set_attribute("rgba_r", pv.FloatAttribute(r_expr))
rgba_bar.set_attribute("rgba_g", pv.FloatAttribute(g_expr))
rgba_bar.set_attribute("rgba_b", pv.FloatAttribute(b_expr))
rgba_bar.set_attribute("rgba_a", pv.FloatAttribute("1.0"))
rgba_bar = pv.AttributeModifier(
    pv.ScalarsToVec4Converter(
        "rgba_r",
        "rgba_g",
        "rgba_b",
        "rgba_a",
        pv.DefaultAttributes.COLOR_RGBA,
    ),
    rgba_bar,
)
# Also publish COLOR_RGB so both bars are visible under the default color view.
rgba_bar = pv.AttributeModifier(
    pv.ScalarsToVec3Converter(
        "rgba_r",
        "rgba_g",
        "rgba_b",
        pv.DefaultAttributes.COLOR_RGB,
    ),
    rgba_bar,
)

rgb_bar = pv.Translate(0.0, gap / 2.0, 0.0, rgb_bar)
rgba_bar = pv.Translate(0.0, -gap / 2.0, 0.0, rgba_bar)

root = pv.Union(rgb_bar, rgba_bar)

viz.Render(root)
