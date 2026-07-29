"""
Slicer project - fuzzy skin gradient (cylinder)
==============================================

Upright cylinder with **FUZZY_SKIN_POINT_DISTANCE** ramping along Z, compiled
to a PrusaSlicer-style **.3mf** for per-volume fuzzy skin settings.

Companion to: docs/source/guides/compilers/slicer-project.md
See also: examples/applications/slicer_settings_mesh/fuzzy_skin_cylinder.py
"""
import os

import pyvcad as pv
import pyvcad_compilers as pvc
import pyvcad_rendering as viz

cylinder_height_mm = 100.0
cylinder_radius_mm = 15.0
edge_buffer_mm = 10.0

half_h = 0.5 * cylinder_height_mm
span = 2.0 * (half_h - edge_buffer_mm)
fuzzy_expr = (
    f"0.4 * clamp((z + {half_h} - {edge_buffer_mm}) / ({span}), 0, 1)"
)

cylinder = pv.Cylinder(pv.Vec3(0, 0, 0), cylinder_radius_mm, cylinder_height_mm)
cylinder.set_attribute(
    pv.DefaultAttributes.FUZZY_SKIN_POINT_DISTANCE,
    pv.FloatAttribute(fuzzy_expr),
)

root = cylinder
viz.Render(root)

_here = os.path.dirname(os.path.abspath(__file__))
out_dir = os.path.join(_here, "output")
os.makedirs(out_dir, exist_ok=True)
out_3mf = os.path.join(out_dir, "fuzzy_skin_cylinder.3mf")

regions = 12
compiler = pvc.PrusaSlicerProjectCompiler(
    root,
    pv.Vec3(0.25, 0.25, 0.25),
    out_3mf,
    regions,
)
compiler.compile()
print("Wrote", out_3mf)
