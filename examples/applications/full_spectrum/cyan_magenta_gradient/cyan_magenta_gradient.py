"""
Cyan-magenta volume-fraction gradient
=====================================

Builds a rectangular prism with pure cyan and magenta end sections and a
linear volume-fraction transition between them. The same design can be
exported to PrusaSlicer ColorMix or Orca FullSpectrum projects.
"""
import os

import pyvcad as pv
import pyvcad_compilers as pvc
import pyvcad_rendering as viz

render = True
export_colormix = True
export_full_spectrum = True

prism_length = 100.0
prism_width = 20.0
prism_height = 20.0
pure_material_width = 5.0

rotate_vertical = True

if pure_material_width < 0.0:
    raise RuntimeError("Pure material width D must be non-negative.")
if 2.0 * pure_material_width >= prism_length:
    raise RuntimeError(
        "Pure material width D must be less than half the prism length."
    )

materials = pv.default_materials
if callable(materials):
    materials = materials()

half_length = 0.5 * prism_length
gradient_start_x = -half_length + pure_material_width
gradient_width = prism_length - 2.0 * pure_material_width

magenta_fraction_expr = (
    f"clamp(0, (x - ({gradient_start_x})) / {gradient_width}, 1)"
)
cyan_fraction_expr = f"1 - ({magenta_fraction_expr})"

prism = pv.RectPrism(
    pv.Vec3(0.0, 0.0, 0.0),
    pv.Vec3(prism_length, prism_width, prism_height),
)
prism.set_attribute(
    pv.DefaultAttributes.VOLUME_FRACTIONS,
    pv.VolumeFractionsAttribute(
        [
            (cyan_fraction_expr, materials.id("cyan")),
            (magenta_fraction_expr, materials.id("magenta")),
        ]
    ),
)

if rotate_vertical:
    prism = pv.Rotate(0,90,0, prism)

root = prism

if render:
    viz.Render(root, materials)

_here = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(_here, "output")
colormix_path = os.path.join(
    output_dir,
    "cyan_magenta_gradient_colormix.3mf",
)
full_spectrum_path = os.path.join(
    output_dir,
    "cyan_magenta_gradient_full_spectrum.3mf",
)

export_voxel_size = pv.Vec3(0.1, 0.1, 0.1)
filaments = [
    {"slot": 1, "color_hex": "#00FFFF"},
    {"slot": 2, "color_hex": "#FF00FF"},
]
volume_fraction_materials = {
    "cyan": 1,
    "magenta": 2,
}
max_palette_size = 20
min_component_percent = 1
max_recipe_components = 2
region_overlap_mm = 0.0


def report_progress(label):
    def _report(progress):
        print("{} progress: {:.1f}%".format(label, 100.0 * progress))
    return _report


if export_colormix:
    os.makedirs(output_dir, exist_ok=True)

    colormix_compiler = pvc.PrusaSlicerProjectCompiler(
        root,
        export_voxel_size,
        colormix_path,
        enable_color_mix=True,
        color_mix_filaments=filaments,
        total_physical_extruders=5,
        volume_fraction_materials=volume_fraction_materials,
        max_palette_size=max_palette_size,
        min_component_percent=min_component_percent,
        max_recipe_components=max_recipe_components,
        region_overlap_mm=region_overlap_mm,
    )
    colormix_compiler.set_progress_callback(report_progress("ColorMix"))
    colormix_compiler.compile()
    print("Wrote", colormix_path)

if export_full_spectrum:
    os.makedirs(output_dir, exist_ok=True)

    full_spectrum_compiler = pvc.FullSpectrumSlicerProjectCompiler(
        root,
        export_voxel_size,
        full_spectrum_path,
        filaments=filaments,
        volume_fraction_materials=volume_fraction_materials,
        max_palette_size=max_palette_size,
        min_component_percent=min_component_percent,
        max_recipe_components=max_recipe_components,
        region_overlap_mm=region_overlap_mm,
        orca_process_profile_path=(
            "0.10mm FastDetail @Prusa XL 5T 0.4.json"
        ),
        orca_default_filament_profile_path="Prusa Generic PLA @XL 5T",
    )
    full_spectrum_compiler.set_progress_callback(
        report_progress("FullSpectrum")
    )
    full_spectrum_compiler.compile()
    print("Wrote", full_spectrum_path)
