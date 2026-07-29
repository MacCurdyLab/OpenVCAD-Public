"""Infill-density settings-mesh benchmark design."""

import pyvcad as pv

import benchmark_utils as bu


edge_buffer_mm = 20.0
infill_min = 5.0
infill_max = 80.0


def dimensions():
    return bu.dimensions()


def infill_expression():
    half_x = 0.5 * bu.BAR_SIZE_X
    span = 2.0 * (half_x - edge_buffer_mm)
    t_expr = f"min(max((x + {half_x} - {edge_buffer_mm}) / ({span}), 0), 1)"
    return (
        f"{infill_min} + ({infill_max} - {infill_min}) * "
        f"({t_expr})"
    )


def build_design():
    bar = pv.RectPrism(
        pv.Vec3(0.0, 0.0, 0.0),
        pv.Vec3(bu.BAR_SIZE_X, bu.BAR_SIZE_Y, bu.BAR_SIZE_Z),
    )
    bar.set_attribute(
        pv.DefaultAttributes.INFILL_DENSITY,
        pv.FloatAttribute(infill_expression()),
    )
    return bar


def sample_summary(root):
    root.prepare(pv.Vec3(1.0, 1.0, 1.0), 6.0)
    half_x = 0.5 * bu.BAR_SIZE_X
    samples = []
    for x in [-half_x + 1.0, 0.0, half_x - 1.0]:
        _, attrs = root.sample(float(x), 0.0, 0.0)
        value = attrs.get_sample(pv.DefaultAttributes.INFILL_DENSITY)
        samples.append("x={:.1f}: infill={:.3f}".format(x, value))
    return samples
