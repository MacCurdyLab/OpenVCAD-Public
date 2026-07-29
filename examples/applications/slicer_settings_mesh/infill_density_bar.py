import pyvcad as pv
import pyvcad_rendering as viz
import pyvcad_compilers as pvc

# Rectangular prism (mm). Long axis is X for the infill gradient.
bar_size_x = 100.0
bar_size_y = 25.0
bar_size_z = 25.0
# End caps (mm): hold infill at 5% and 80%; ramp in the center span.
edge_buffer_mm = 10.0

half_x = 0.5 * bar_size_x
span = 2.0 * (half_x - edge_buffer_mm)
# Compiler maps infill_density to PrusaSlicer fill_density as integer percent (0–100).
infill_expr = (
    f"5 + 75 * clamp((x + {half_x} - {edge_buffer_mm}) / ({span}), 0, 1)"
)

bar = pv.RectPrism(pv.Vec3(0, 0, 0), pv.Vec3(bar_size_x, bar_size_y, bar_size_z))
bar.set_attribute(pv.DefaultAttributes.INFILL_DENSITY, pv.FloatAttribute(infill_expr))

root = bar
viz.Render(root)

regions = 12
compiler = pvc.PrusaSlicerProjectCompiler(
    root,
    pv.Vec3(0.25, 0.25, 0.25),
    "infill_density_bar.3mf",
    regions,
)
compiler.compile()
