import pyvcad as pv
import pyvcad_rendering as viz

# Manual LW-PLA flow compensation using a single AttributeModifier.
bar_length = 180.0
bar_width = 12.0
bar_height = 12.0
temperature_expr = "max(min((x/3 + 236), 256), 220)"

foaming_pla_flow_compensation = [
    (220, 1.42),
    (224, 1.23),
    (228, 1.08),
    (232, 0.98),
    (236, 0.86),
    (240, 0.76),
    (244, 0.72),
    (248, 0.69),
    (252, 0.67),
    (256, 0.66),
]

flow_entries = [pv.LookupTableEntry(kv[0], kv[0], kv[1])
                for kv in foaming_pla_flow_compensation]
flow_converter = pv.LookupTableConverter(
    input_attributes=[pv.DefaultAttributes.TEMPERATURE],
    output_attributes=[pv.DefaultAttributes.FLOW_RATE],
    entries=flow_entries,
    mode=pv.InterpolationMode.LINEAR,
)

bar = pv.RectPrism(pv.Vec3(0, 0, 0), pv.Vec3(bar_length, bar_width, bar_height))
bar.set_attribute(pv.DefaultAttributes.TEMPERATURE,
                  pv.FloatAttribute(temperature_expr))

root = pv.AttributeModifier(flow_converter, bar)
viz.Render(root)
