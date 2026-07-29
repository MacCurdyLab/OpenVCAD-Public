import pyvcad as pv
import pyvcad_rendering as viz
import pyvcad_attribute_resolver as resolver

# The resolver replaces the manual lookup-table wiring from Lesson 1.
resolver.clear_conversions()
resolver.register_pla_conversions()

bar_length = 180.0
bar_width = 12.0
bar_height = 12.0
temperature_expr = "max(min((x/3 + 236), 256), 220)"

bar = pv.RectPrism(pv.Vec3(0, 0, 0), pv.Vec3(bar_length, bar_width, bar_height))
bar.set_attribute(pv.DefaultAttributes.TEMPERATURE,
                  pv.FloatAttribute(temperature_expr))

root = resolver.adapt(bar, ["flow_rate"], tags=["foaming_pla"])
viz.Render(root)
