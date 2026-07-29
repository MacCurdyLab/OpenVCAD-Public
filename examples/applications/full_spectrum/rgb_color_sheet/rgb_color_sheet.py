"""
RGB color sheet compiler example
================================

Builds a single connected sheet of square RGB swatches. The same object carries
both COLOR_RGB and COLOR_RGBA so it can be compiled either as an Orca
FullSpectrum slicer project or as a ColorInkjet PNG stack.
"""
import math
import os
import shutil

import pyvcad as pv
import pyvcad_compilers as pvc
import pyvcad_rendering as viz

render = True
export_full_spectrum = True
export_colormix = True
export_inkjet = False

rgb_levels = 3
swatch_size = 10.0
sheet_thickness = 8
# Each blue level is a red-by-green panel. Keep panel_gap at 0.0 if you want
# the swatch sheet to remain one connected object.
blue_panels_per_row = 3
panel_gap = 0.0
voxel_size = pv.Vec3(0.25, 0.25, 0.25)

max_palette_size = 27
min_component_percent = 10
max_recipe_components = 3
region_overlap_mm = 0.5
orca_process_profile = "0.10mm FastDetail @Prusa XL 5T 0.4.json"
orca_filament_profile = "Prusa Generic PLA @XL 5T"

_here = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(_here, "output")
full_spectrum_path = os.path.join(output_dir, "rgb_color_sheet_full_spectrum.3mf")
colormix_path = os.path.join(output_dir, "rgb_color_sheet_colormix.3mf")
inkjet_output_dir = os.path.join(output_dir, "rgb_color_sheet_inkjet")
inkjet_prefix = "slice_"


def channel_value(index):
    if rgb_levels <= 1:
        return 0.0
    return index / (rgb_levels - 1)


def make_swatch(red_index, green_index, blue_index):
    panels_per_row = max(1, blue_panels_per_row)
    panel_column = blue_index % panels_per_row
    panel_row = blue_index // panels_per_row
    panel_count_x = min(rgb_levels, panels_per_row)
    panel_count_y = int(math.ceil(rgb_levels / panels_per_row))
    panel_pitch = rgb_levels * swatch_size + panel_gap

    sheet_width = panel_count_x * rgb_levels * swatch_size
    sheet_height = panel_count_y * rgb_levels * swatch_size
    if panel_count_x > 1:
        sheet_width += (panel_count_x - 1) * panel_gap
    if panel_count_y > 1:
        sheet_height += (panel_count_y - 1) * panel_gap

    x = (
        panel_column * panel_pitch
        + (red_index + 0.5) * swatch_size
        - 0.5 * sheet_width
    )
    y = (
        panel_row * panel_pitch
        + (green_index + 0.5) * swatch_size
        - 0.5 * sheet_height
    )

    red = channel_value(red_index)
    green = channel_value(green_index)
    blue = channel_value(blue_index)

    swatch = pv.RectPrism(
        pv.Vec3(x, y, 0.5 * sheet_thickness),
        pv.Vec3(swatch_size, swatch_size, sheet_thickness),
    )
    swatch.set_attribute(
        pv.DefaultAttributes.COLOR_RGB,
        pv.Vec3Attribute(red, green, blue),
    )
    swatch.set_attribute(
        pv.DefaultAttributes.COLOR_RGBA,
        pv.Vec4Attribute(red, green, blue, 1.0),
    )
    return swatch


root = pv.BBoxUnion()

for blue_index in range(rgb_levels):
    for green_index in range(rgb_levels):
        for red_index in range(rgb_levels):
            root.add_child(make_swatch(red_index, green_index, blue_index))

if render:
    viz.Render(root)

os.makedirs(output_dir, exist_ok=True)


def report_progress(label):
    def _report(progress):
        print("{} progress: {:.1f}%".format(label, 100.0 * progress))
    return _report


if export_full_spectrum:
    full_spectrum_compiler = pvc.FullSpectrumSlicerProjectCompiler(
        root,
        voxel_size,
        full_spectrum_path,
        max_palette_size=max_palette_size,
        min_component_percent=min_component_percent,
        max_recipe_components=max_recipe_components,
        region_overlap_mm=region_overlap_mm,
        orca_process_profile_path=orca_process_profile,
        orca_default_filament_profile_path=orca_filament_profile,
    )
    full_spectrum_compiler.set_progress_callback(report_progress("FullSpectrum"))
    full_spectrum_compiler.compile()
    print("Wrote", full_spectrum_path)

if export_colormix:
    compiler = pvc.PrusaSlicerProjectCompiler(
        root,
        voxel_size,
        colormix_path,
        enable_color_mix=True,
        color_mix_recipe_preset="expanded",
        max_palette_size=max_palette_size,
        min_component_percent=min_component_percent,
        max_recipe_components=max_recipe_components,
        region_overlap_mm=region_overlap_mm,
    )
    compiler.set_progress_callback(report_progress("PrusaSlicerProject"))
    compiler.compile()
    print("Wrote", colormix_path)

if export_inkjet:
    inkjet_voxel_size = pv.Vec3(0.0423, 0.0846, 0.027)
    if os.path.isdir(inkjet_output_dir):
        shutil.rmtree(inkjet_output_dir)
    os.makedirs(inkjet_output_dir, exist_ok=True)

    icc_profiles_dir = os.path.join(
        os.path.dirname(os.path.abspath(pvc.__file__)),
        "icc_profiles",
    )
    if not os.path.isdir(icc_profiles_dir):
        icc_profiles_dir = os.path.abspath(
            os.path.join(_here, "..", "..", "..", "compilers", "icc_profiles")
        )
    pvc.ColorPipeline.set_icc_resource_path(icc_profiles_dir)

    inkjet_compiler = pvc.ColorInkjetCompiler(
        root,
        inkjet_voxel_size,
        inkjet_output_dir,
        inkjet_prefix,
        "default",
    )
    inkjet_compiler.set_progress_callback(report_progress("ColorInkjet"))
    inkjet_compiler.compile()
    print("Wrote", inkjet_output_dir)
