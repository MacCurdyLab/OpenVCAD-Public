import pyvcad as pv
import pyvcad_rendering as viz
import pyvcad_attribute_resolver as resolver

# Start from design intent (density) and let the resolver derive the
# machine-facing attributes needed by the foaming PLA workflow.
resolver.clear_conversions()
resolver.register_pla_conversions()

bar_length = 180.0
bar_width = 12.0
bar_height = 12.0
density_min = 0.50
density_max = 1.00
density_slope = (density_min - density_max) / bar_length
density_offset = (density_min + density_max) / 2.0
density_expr = (
    f"max(min({density_slope:.8f} * x + {density_offset:.8f}, "
    f"{density_max:.8f}), {density_min:.8f})"
)

bar = pv.RectPrism(pv.Vec3(0, 0, 0), pv.Vec3(bar_length, bar_width, bar_height))
bar.set_attribute(pv.DefaultAttributes.DENSITY, pv.FloatAttribute(density_expr))

root = resolver.adapt(bar, ["temperature", "flow_rate"], tags=["foaming_pla"])
viz.Render(root)
