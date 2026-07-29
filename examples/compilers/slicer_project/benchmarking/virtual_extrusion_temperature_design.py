"""Foaming PLA virtual-extrusion benchmark design."""

import pyvcad as pv
import pyvcad_attribute_resolver as resolver

import benchmark_utils as bu


temperature_min_c = 220.0
temperature_max_c = 256.0


def dimensions():
    return bu.dimensions()


def temperature_expression():
    half_x = 0.5 * bu.BAR_SIZE_X
    t_expr = f"min(max((x + {half_x}) / {bu.BAR_SIZE_X}, 0), 1)"
    return (
        f"{temperature_min_c} + ({temperature_max_c} - {temperature_min_c}) * "
        f"({t_expr})"
    )


def build_design():
    resolver.clear_conversions()
    resolver.register_pla_conversions()

    bar = pv.RectPrism(
        pv.Vec3(0.0, 0.0, 0.0),
        pv.Vec3(bu.BAR_SIZE_X, bu.BAR_SIZE_Y, bu.BAR_SIZE_Z),
    )
    bar.set_attribute(
        pv.DefaultAttributes.TEMPERATURE,
        pv.FloatAttribute(temperature_expression()),
    )
    return resolver.adapt(bar, ["flow_rate"], tags=["foaming_pla"])


def sample_summary(root):
    root.prepare(pv.Vec3(1.0, 1.0, 1.0), 6.0)
    half_x = 0.5 * bu.BAR_SIZE_X
    samples = []
    for x in [-half_x + 1.0, 0.0, half_x - 1.0]:
        _, attrs = root.sample(float(x), 0.0, 0.0)
        temperature = attrs.get_sample(pv.DefaultAttributes.TEMPERATURE)
        flow_rate = attrs.get_sample(pv.DefaultAttributes.FLOW_RATE)
        samples.append(
            "x={:.1f}: temperature={:.3f}, flow_rate={:.6f}".format(
                x, temperature, flow_rate
            )
        )
    return samples
