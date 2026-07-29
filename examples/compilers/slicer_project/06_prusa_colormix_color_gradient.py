"""
Slicer project - PrusaSlicer ColorMix color gradient
====================================================

Rectangular color swatch with **COLOR_RGB** ramping along X, compiled to a
PrusaSlicer ColorMix **.3mf** with virtual mixed-filament materials.

Companion to: docs/source/guides/compilers/slicer-project.md
"""
import os

import pyvcad as pv
import pyvcad_compilers as pvc
import pyvcad_rendering as viz

bar_size_x = 60.0
bar_size_y = 18.0
bar_size_z = 12.0

half_x = 0.5 * bar_size_x
t_expr = f"clamp((x + {half_x}) / {bar_size_x}, 0, 1)"

# Design-space RGB target: cyan on the left, magenta on the right.
red_expr = t_expr
green_expr = f"1 - {t_expr}"
blue_expr = "1"

bar = pv.RectPrism(pv.Vec3(0, 0, 0), pv.Vec3(bar_size_x, bar_size_y, bar_size_z))
bar.set_attribute(
    pv.DefaultAttributes.COLOR_RGB,
    pv.Vec3Attribute(red_expr, green_expr, blue_expr),
)

root = bar

viz.Render(root)

_here = os.path.dirname(os.path.abspath(__file__))
out_dir = os.environ.get("OPENVCAD_SLICER_PROJECT_OUTPUT_DIR")
if out_dir is None:
    out_dir = os.path.join(_here, "output")
os.makedirs(out_dir, exist_ok=True)
out_3mf = os.path.join(out_dir, "prusa_colormix_color_gradient.3mf")

compiler = pvc.PrusaSlicerProjectCompiler(
    root,
    pv.Vec3(0.25, 0.25, 0.25),
    out_3mf,
    enable_color_mix=True,
    color_mix_recipe_preset="expanded",
    max_palette_size=10,
    min_component_percent=25,
    max_recipe_components=3,
    region_overlap_mm=0.0,
)

def report_progress(progress):
    print(f"Slicer export progress: {progress * 100}%")
compiler.set_progress_callback(report_progress)

compiler.compile()
print("Wrote", out_3mf)
