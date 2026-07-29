"""Functionally defined full-gamut Half-toning benchmark design."""

import pyvcad as pv

import benchmark_utils as bu


def dimensions():
    return bu.dimensions()


def color_expressions():
    half_x = 0.5 * bu.BAR_SIZE_X
    half_y = 0.5 * bu.BAR_SIZE_Y
    half_z = 0.5 * bu.BAR_SIZE_Z
    red = f"min(max((x + {half_x}) / {bu.BAR_SIZE_X}, 0), 1)"
    green = f"min(max((y + {half_y}) / {bu.BAR_SIZE_Y}, 0), 1)"
    blue = f"min(max((z + {half_z}) / {bu.BAR_SIZE_Z}, 0), 1)"
    return red, green, blue


def build_design():
    bar = pv.RectPrism(
        pv.Vec3(0.0, 0.0, 0.0),
        pv.Vec3(bu.BAR_SIZE_X, bu.BAR_SIZE_Y, bu.BAR_SIZE_Z),
    )
    red, green, blue = color_expressions()
    bar.set_attribute(
        pv.DefaultAttributes.COLOR_RGB,
        pv.Vec3Attribute(red, green, blue),
    )
    return bar


def sample_summary(root):
    root.prepare(pv.Vec3(1.0, 1.0, 1.0), 6.0)
    half_x = 0.5 * bu.BAR_SIZE_X
    half_y = 0.5 * bu.BAR_SIZE_Y
    half_z = 0.5 * bu.BAR_SIZE_Z
    samples = []
    points = [
        (-half_x + 1.0, -half_y + 1.0, -half_z + 1.0),
        (half_x - 1.0, -half_y + 1.0, -half_z + 1.0),
        (-half_x + 1.0, half_y - 1.0, -half_z + 1.0),
        (-half_x + 1.0, -half_y + 1.0, half_z - 1.0),
        (0.0, 0.0, 0.0),
        (half_x - 1.0, half_y - 1.0, half_z - 1.0),
    ]
    for x, y, z in points:
        _, attrs = root.sample(float(x), float(y), float(z))
        color = attrs.get_sample(pv.DefaultAttributes.COLOR_RGB)
        samples.append(
            "x={:.1f}, y={:.1f}, z={:.1f}: rgb=({:.3f}, {:.3f}, {:.3f})".format(
                x, y, z, color.x, color.y, color.z
            )
        )
    return samples
