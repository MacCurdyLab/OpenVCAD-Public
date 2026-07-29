"""
Slicer project - infill density gradient (bar)
============================================

Rectangular bar with **INFILL_DENSITY** ramping along X, compiled to a **.3mf**
with per-volume **fill_density** metadata for PrusaSlicer.

Companion to: docs/source/guides/compilers/slicer-project.md
See also: examples/applications/slicer_settings_mesh/infill_density_bar.py
"""
import os

import pyvcad as pv
import pyvcad_compilers as pvc
import pyvcad_rendering as viz

bar_size_x = 100.0
bar_size_y = 25.0
bar_size_z = 25.0
edge_buffer_mm = 10.0

half_x = 0.5 * bar_size_x
span = 2.0 * (half_x - edge_buffer_mm)
infill_expr = (
    f"5 + 75 * clamp((x + {half_x} - {edge_buffer_mm}) / ({span}), 0, 1)"
)

bar = pv.RectPrism(pv.Vec3(0, 0, 0), pv.Vec3(bar_size_x, bar_size_y, bar_size_z))
bar.set_attribute(pv.DefaultAttributes.INFILL_DENSITY, pv.FloatAttribute(infill_expr))

root = bar
viz.Render(root)

_here = os.path.dirname(os.path.abspath(__file__))
out_dir = os.path.join(_here, "output")
os.makedirs(out_dir, exist_ok=True)
out_3mf = os.path.join(out_dir, "infill_density_bar.3mf")

regions = 12
compiler = pvc.PrusaSlicerProjectCompiler(
    root,
    pv.Vec3(0.25, 0.25, 0.25),
    out_3mf,
    regions,
)
compiler.compile()
print("Wrote", out_3mf)
