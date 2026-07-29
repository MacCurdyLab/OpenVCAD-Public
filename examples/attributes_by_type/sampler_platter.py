import math

import pyvcad as pv
import pyvcad_rendering as viz

materials = pv.default_materials

object_spacing = 32.0
object_positions = [
    -3.0 * object_spacing,
    -2.0 * object_spacing,
    -1.0 * object_spacing,
    0.0,
    1.0 * object_spacing,
    2.0 * object_spacing,
    3.0 * object_spacing,
]


def translate_to_line(index, node):
    return pv.Translate(object_positions[index], 0.0, 0.0, node)


def clamp01_expr(expr):
    return f"clamp(({expr}), 0, 1)"


def smoothstep_expr(t_expr, start, end):
    u_expr = clamp01_expr(f"(({t_expr}) - {start}) / ({end} - {start})")
    return f"(({u_expr}) * ({u_expr}) * (3 - 2 * ({u_expr})))"


def mix_expr(a_expr, b_expr, weight_expr):
    return f"(({a_expr}) * (1 - ({weight_expr})) + ({b_expr}) * ({weight_expr}))"


def palette_channel_expr(channel_index, t_expr, stops):
    expr = str(stops[0][1][channel_index])
    for start_stop, end_stop in zip(stops[:-1], stops[1:]):
        weight_expr = smoothstep_expr(t_expr, start_stop[0], end_stop[0])
        expr = mix_expr(expr, str(end_stop[1][channel_index]), weight_expr)
    return expr


# SHORE_HARDNESS: a sphere with a radial gradient, soft at the core and
# harder near the surface. Values are Shore A.
shore_radius = 9.0
shore_min = 40.0
shore_max = 95.0
shore_expr = (
    f"{shore_min} + ({shore_max} - {shore_min}) * "
    f"{clamp01_expr(f'r / {shore_radius}')}"
)
shore_sphere = pv.Sphere(pv.Vec3(0.0, 0.0, 0.0), shore_radius)
shore_sphere.set_attribute(
    pv.DefaultAttributes.SHORE_HARDNESS,
    pv.FloatAttribute(shore_expr),
)

# MODULUS: a rectangular prism with a signed-distance skin gradient. The
# surface is stiff and the interior falls toward a softer polymer modulus.
modulus_size = 18.0
modulus_skin_thickness = 3.0
modulus_min_mpa = 10.0
modulus_max_mpa = 100.0
modulus_expr = (
    f"{modulus_min_mpa} + ({modulus_max_mpa} - {modulus_min_mpa}) * "
    f"exp(d / {modulus_skin_thickness})"
)
modulus_prism = pv.RectPrism(
    pv.Vec3(0.0, 0.0, 0.0),
    pv.Vec3(modulus_size, modulus_size, modulus_size),
)
modulus_prism.set_attribute(
    pv.DefaultAttributes.MODULUS,
    pv.FloatAttribute(modulus_expr),
)

# TOUGHNESS: a cone with a nonlinear Gaussian-like band through the middle.
# Values are in MJ/m^3 to match the mechanical-property resolver examples.
toughness_height = 18.0
toughness_angle = math.radians(30.0)
toughness_sigma = 3.2
toughness_min_mj_per_m3 = 2.0
toughness_max_mj_per_m3 = 4.0
toughness_expr = (
    f"{toughness_min_mj_per_m3} + "
    f"({toughness_max_mj_per_m3} - {toughness_min_mj_per_m3}) * "
    f"exp(-((y + {0.5 * toughness_height})^2) / (2 * {toughness_sigma}^2))"
)
toughness_cone = pv.Cone(toughness_angle, toughness_height)
toughness_cone.set_attribute(
    pv.DefaultAttributes.TOUGHNESS,
    pv.FloatAttribute(toughness_expr),
)
toughness_cone = pv.Translate(0.0, 0.5 * toughness_height, 0.0, toughness_cone)

# INFILL_DENSITY: a cylinder with periodic bands along Z. Slicer examples map
# this attribute to PrusaSlicer fill_density, so values are percentages.
infill_radius = 9.0
infill_height = 18.0
infill_period = 7.5
infill_mid_percent = 45.0
infill_amplitude_percent = 35.0
infill_expr = (
    f"{infill_mid_percent} + {infill_amplitude_percent} * "
    f"sin(2 * {math.pi} * (z + {0.5 * infill_height}) / {infill_period})"
)
infill_cylinder = pv.Cylinder(
    pv.Vec3(0.0, 0.0, 0.0),
    infill_radius,
    infill_height,
)
infill_cylinder.set_attribute(
    pv.DefaultAttributes.INFILL_DENSITY,
    pv.FloatAttribute(infill_expr),
)

# TEMPERATURE: a text glyph with a simple linear gradient through its
# extrusion depth. Values are common extrusion temperatures in degrees C.
temperature_depth = 5.0
temperature_min_c = 205.0
temperature_max_c = 235.0
temperature_expr = (
    f"{temperature_min_c} + ({temperature_max_c} - {temperature_min_c}) * "
    f"{clamp01_expr(f'(z + {0.5 * temperature_depth}) / {temperature_depth}')}"
)
temperature_text = pv.Text(
    "+",
    16.0,
    temperature_depth,
    pv.FontAspect.Regular,
    "Arial",
    pv.HorizontalAlignment.Center,
    pv.VerticalAlignment.Center,
)
temperature_text.set_attribute(
    pv.DefaultAttributes.TEMPERATURE,
    pv.FloatAttribute(temperature_expr),
)

# COLOR_RGB: a torus with an angular blue-orange-yellow sweep. The palette is
# intentionally colorful while preserving useful light/dark contrast.
color_t_expr = clamp01_expr(f"(phic + {math.pi}) / (2 * {math.pi})")
color_stops = [
    (0.0, (0.02, 0.20, 0.85)),
    (0.5, (0.95, 0.34, 0.06)),
    (1.0, (1.00, 0.82, 0.05)),
]
color_torus = pv.Torus(7.0, 2.5)
color_torus.set_attribute(
    pv.DefaultAttributes.COLOR_RGB,
    pv.Vec3Attribute(
        palette_channel_expr(0, color_t_expr, color_stops),
        palette_channel_expr(1, color_t_expr, color_stops),
        palette_channel_expr(2, color_t_expr, color_stops),
    ),
)

# VOLUME_FRACTIONS: a strut that blends between blue and yellow default
# materials. These default colors remain high-contrast in grayscale printouts.
vf_half_length = 9.0
vf_t_expr = clamp01_expr(f"(x + {vf_half_length}) / ({2.0 * vf_half_length})")
vf_strut = pv.Strut(
    pv.Vec3(-vf_half_length, 0.0, 0.0),
    pv.Vec3(vf_half_length, 0.0, 0.0),
    3.0,
)
vf_strut.set_attribute(
    pv.DefaultAttributes.VOLUME_FRACTIONS,
    pv.VolumeFractionsAttribute(
        [
            (f"1.0 - ({vf_t_expr})", materials.id("green")),
            (vf_t_expr, materials.id("magenta")),
        ]
    ),
)

root = pv.BBoxUnion(
    [
        translate_to_line(0, shore_sphere),
        translate_to_line(1, modulus_prism),
        translate_to_line(2, toughness_cone),
        translate_to_line(3, infill_cylinder),
        translate_to_line(4, temperature_text),
        translate_to_line(5, color_torus),
        translate_to_line(6, vf_strut),
    ]
)

viz.Render(root, materials)
