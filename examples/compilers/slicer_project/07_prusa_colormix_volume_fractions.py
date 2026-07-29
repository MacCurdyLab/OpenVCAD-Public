"""
Slicer project - PrusaSlicer ColorMix volume fractions
=====================================================

Rectangular material swatch with **VOLUME_FRACTIONS** ramping from red to blue
along X, compiled to a PrusaSlicer ColorMix **.3mf** with direct mixed-filament
recipes.

Companion to: docs/source/guides/compilers/slicer-project.md
"""
import os

import pyvcad as pv
import pyvcad_compilers as pvc
import pyvcad_rendering as viz

materials = pv.default_materials
if callable(materials):
    materials = materials()

bar_size_x = 60.0
bar_size_y = 18.0
bar_size_z = 12.0

half_x = 0.5 * bar_size_x
blue_fraction_expr = f"(x + {half_x}) / {bar_size_x}"
red_fraction_expr = f"1 - ({blue_fraction_expr})"

bar = pv.RectPrism(pv.Vec3(0, 0, 0), pv.Vec3(bar_size_x, bar_size_y, bar_size_z))
bar.set_attribute(
    pv.DefaultAttributes.VOLUME_FRACTIONS,
    pv.VolumeFractionsAttribute(
        [
            (red_fraction_expr, materials.id("red")),
            (blue_fraction_expr, materials.id("blue")),
        ]
    ),
)

root = bar

viz.Render(root, materials)

_here = os.path.dirname(os.path.abspath(__file__))
out_dir = os.environ.get("OPENVCAD_SLICER_PROJECT_OUTPUT_DIR")
if out_dir is None:
    out_dir = os.path.join(_here, "output")
os.makedirs(out_dir, exist_ok=True)
out_3mf = os.path.join(out_dir, "prusa_colormix_volume_fractions.3mf")

compiler = pvc.PrusaSlicerProjectCompiler(
    root,
    pv.Vec3(0.25, 0.25, 0.25),
    out_3mf,
    enable_color_mix=True,
    total_physical_extruders=5,
    color_mix_filaments=[
        {"slot": 1, "color_hex": "#FF0000"},
        {"slot": 2, "color_hex": "#0000FF"},
    ],
    volume_fraction_materials={"red": 1, "blue": 2},
    max_palette_size=10,
    min_component_percent=1,
    max_recipe_components=3,
    region_overlap_mm=0.0,
)

def report_progress(progress):
    print(f"Slicer export progress: {progress * 100}%")
compiler.set_progress_callback(report_progress)

compiler.compile()
print("Wrote", out_3mf)
