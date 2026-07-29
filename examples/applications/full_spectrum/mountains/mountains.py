import os
import shutil

import pyvcad as pv
import pyvcad_rendering as viz
import pyvcad_compilers as pvc
import pyvcad_attribute_resolver as resolver

# https://openclipart.org/detail/255870/flat-shaded-mountains-scene

image_name = "mountains_v2.png"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_PATH = os.path.join(SCRIPT_DIR, image_name)

render = True
export_colormix = False
export_full_spectrum = False
export_inkjet = False


# Each pixel becomes a voxel cell in x/y, and the single image is repeated
# through z until depth_mm is reached.
image_voxel_size = pv.Vec3(0.075, 0.075, 0.075)
depth_mm = 10.0

png_loader = pv.PNGLoader.FromImage(
    IMAGE_PATH,
    image_voxel_size,
    depth_mm,
    pv.PNGColorMode.COLOR_RGB,
    center=True,
)
color_volume = png_loader.as_rgb_volume()

carrier_min, carrier_max = color_volume.bounding_box()
carrier = pv.RectPrism.FromMinAndMax(carrier_min, carrier_max)
carrier.set_attribute(pv.DefaultAttributes.COLOR_RGB, pv.Vec3Attribute(color_volume))

root = carrier

if render:
    viz.Render(root)

_here = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(_here, "output")
colormix_path = os.path.join(output_dir, image_name.replace(".png", "_colormix.3mf"))
full_spectrum_path = os.path.join(output_dir, image_name.replace(".png", "_full_spectrum.3mf"))
inkjet_output_dir = os.path.join(output_dir, "mountains_inkjet")
inkjet_prefix = "slice_"

slicer_export_voxel_size = pv.Vec3(0.20, 0.20, 0.20)
max_palette_size = 32
min_component_percent = 15
max_recipe_components = 3
region_overlap_mm = 0.0
color_mix_recipe_preset = "expanded"

def report_progress(label):
    def _report(progress):
        print("{} progress: {:.1f}%".format(label, 100.0 * progress))
    return _report

if export_colormix:
    os.makedirs(output_dir, exist_ok=True)
    compiler = pvc.PrusaSlicerProjectCompiler(
        root,
        slicer_export_voxel_size,
        colormix_path,
        enable_color_mix=True,
        color_mix_recipe_preset=color_mix_recipe_preset,
        max_palette_size=max_palette_size,
        min_component_percent=min_component_percent,
        max_recipe_components=max_recipe_components,
        region_overlap_mm=region_overlap_mm,
    )

    compiler.set_progress_callback(report_progress("ColorMix"))
    compiler.compile()
    print("Wrote", colormix_path)

if export_full_spectrum:
    orca_process_profile = "0.10mm FastDetail @Prusa XL 5T 0.4.json"
    orca_filament_profile = "Prusa Generic PLA @XL 5T"

    os.makedirs(output_dir, exist_ok=True)
    full_spectrum_compiler = pvc.FullSpectrumSlicerProjectCompiler(
        root,
        slicer_export_voxel_size,
        full_spectrum_path,
        max_palette_size=max_palette_size,
        min_component_percent=min_component_percent,
        max_recipe_components=max_recipe_components,
        region_overlap_mm=region_overlap_mm,
        orca_process_profile_path=orca_process_profile,
        orca_default_filament_profile_path=orca_filament_profile,
        color_mix_recipe_preset=color_mix_recipe_preset,
    )
    full_spectrum_compiler.set_progress_callback(report_progress("FullSpectrum"))
    full_spectrum_compiler.compile()
    print("Wrote", full_spectrum_path)

if export_inkjet:
    inkjet_voxel_size = pv.Vec3(0.0423, 0.0846, 0.027)
    if os.path.isdir(inkjet_output_dir):
        shutil.rmtree(inkjet_output_dir)
    os.makedirs(inkjet_output_dir, exist_ok=True)

    resolver.register_rgb_to_rgba_conversion(alpha=1.0)
    inkjet_root = resolver.adapt(
        root,
        [pv.DefaultAttributes.COLOR_RGBA],
        tags=["generic_color"],
    )

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
        inkjet_root,
        inkjet_voxel_size,
        inkjet_output_dir,
        inkjet_prefix,
        "default",
        pvc.ColorInkjetExportMode.DITHERED_3D
    )
    inkjet_compiler.set_progress_callback(report_progress("ColorInkjet"))
    inkjet_compiler.compile()
    print("Wrote", inkjet_output_dir)
