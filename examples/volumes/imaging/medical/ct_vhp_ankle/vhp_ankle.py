import pyvcad as pv
import pyvcad_medical as med
import pyvcad_compilers as pvc
import pyvcad_rendering as viz
import pyvcad_attribute_resolver as resolver

# Select "mechanical" or "volume_fractions".
MAPPING_MODE = "volume_fractions"

render = False
# Exports the current VOLUME_FRACTIONS with MaterialInkjetCompiler.
# In "mechanical" mode, those fractions come from modulus/toughness; in
# "volume_fractions" mode, they come from the direct HU material mapping.
export_material_inkjet = True
export_visual = False
use_grayscale_color_palette = True
voxel_size = pv.Vec3(0.0423,0.0846,0.027)
liquid_keepout = 1.5 # mm
dicom_path = "dicom_ankle/"
mesh_path = "ankle.obj"
prefix = "ankle_"

# RadioMatrix/Vero mapping controls.
RADIO_MATRIX_MATERIAL = "RadioMatrix"
VERO_MATERIAL = "VeroClear"

# Scanner and mounting controls. X is the print and scanner alignment axis.
# The foot is scaled to this X length before the mounting bar is added, so the
# scanner field of view remains independent of the clamping geometry.
FOOT_X_LENGTH = 45.0 # mm
ENABLE_MOUNTING_BAR = True
MOUNTING_BAR_EXTENSION_RATIO = 0.25
# 3 mm at the default 50 mm foot length. Increase only if more attachment is
# needed, without changing the exposed clamping length.
MOUNTING_BAR_EMBEDDED_RATIO = 0.08
MOUNTING_BAR_CROSS_SECTION_RATIO = 0.05

# Keep exports for differently sized scanner phantoms separate. Replace the
# decimal point to keep the size label filename-friendly (for example, x45p5mm).
foot_x_length_slug = "{:g}".format(FOOT_X_LENGTH).replace(".", "p")
material_output_dir = "output/ankle_material_x{}mm/".format(foot_x_length_slug)
visual_output_dir = "output/ankle_visual_x{}mm/".format(foot_x_length_slug)

# One-time histogram analysis of DICOM voxels enclosed by ankle.obj found
# these rounded 5th and 99th percentile cutoffs. They give the soft tissue and
# internal bone structures the full available RadioMatrix/VeroClear gradient
# without letting a small number of air and high-density outliers flatten it.
VOLUME_FRACTION_HU_MIN = -100.0
VOLUME_FRACTION_HU_MAX = 1000.0

if MAPPING_MODE not in ("mechanical", "volume_fractions"):
    raise ValueError(
        "MAPPING_MODE must be 'mechanical' or 'volume_fractions'."
    )

# The RadioMatrix material definitions contain RadioMatrix and the selected
# Vero material; the mechanical mapping continues to use its original palette.
materials = (
    pv.default_materials
    if MAPPING_MODE == "mechanical"
    else pv.j750_materials
)
# The mechanical palette has no J750 VeroClear entry, so use its equivalent
# transparent material while preserving the original mechanical mapping.
MOUNTING_MATERIAL = (
    VERO_MATERIAL
    if materials.contains(VERO_MATERIAL)
    else "clear"
)
RIGID_MATERIAL = "red"
SOFT_MATERIAL = "green"
LIQUID_MATERIAL = "liquid"

# Maps Houndsfield unit ranges to properties
hu_prop_map = [
    [[-2000, 0],     [10**-0.653, 0.344]],
    [[0, 150],       [10**-0.036, 0.9]],
    [[150, 300],     [10**2, 2.2]],
    [[300, 3000],    [10**2.95, 4.45]]
]

warm_hu_color_map = [
    pv.LookupTableEntry(-1024, pv.Vec4(0.00, 0.00, 0.00, 0.00)),
    pv.LookupTableEntry(-500,  pv.Vec4(0.00, 0.00, 0.00, 0.00)),
    pv.LookupTableEntry(-200,  pv.Vec4(0.95, 0.76, 0.45, 0.008)),
    pv.LookupTableEntry(-80,   pv.Vec4(1.00, 0.62, 0.48, 0.012)),
    pv.LookupTableEntry(0,     pv.Vec4(0.86, 0.42, 0.36, 0.018)),
    pv.LookupTableEntry(45,    pv.Vec4(0.72, 0.22, 0.25, 0.024)),
    pv.LookupTableEntry(100,   pv.Vec4(0.82, 0.55, 0.74, 0.035)),
    pv.LookupTableEntry(180,   pv.Vec4(0.96, 0.72, 0.54, 0.055)),
    pv.LookupTableEntry(300,   pv.Vec4(1.00, 0.88, 0.62, 0.130)),
    pv.LookupTableEntry(700,   pv.Vec4(0.98, 0.96, 0.84, 0.420)),
    pv.LookupTableEntry(1200,  pv.Vec4(1.00, 1.00, 0.96, 0.680)),
    pv.LookupTableEntry(3000,  pv.Vec4(1.00, 1.00, 1.00, 0.780)),
]

grayscale_hu_color_map = [
    pv.LookupTableEntry(-1024, pv.Vec4(0.00, 0.00, 0.00, 0.00)),
    pv.LookupTableEntry(-500,  pv.Vec4(0.00, 0.00, 0.00, 0.00)),
    pv.LookupTableEntry(-200,  pv.Vec4(0.22, 0.22, 0.22, 0.008)),
    pv.LookupTableEntry(-80,   pv.Vec4(0.30, 0.30, 0.30, 0.012)),
    pv.LookupTableEntry(0,     pv.Vec4(0.38, 0.38, 0.38, 0.018)),
    pv.LookupTableEntry(45,    pv.Vec4(0.46, 0.46, 0.46, 0.024)),
    pv.LookupTableEntry(100,   pv.Vec4(0.54, 0.54, 0.54, 0.035)),
    pv.LookupTableEntry(180,   pv.Vec4(0.64, 0.64, 0.64, 0.055)),
    pv.LookupTableEntry(300,   pv.Vec4(0.74, 0.74, 0.74, 0.130)),
    pv.LookupTableEntry(700,   pv.Vec4(0.86, 0.86, 0.86, 0.420)),
    pv.LookupTableEntry(1200,  pv.Vec4(0.94, 0.94, 0.94, 0.680)),
    pv.LookupTableEntry(3000,  pv.Vec4(1.00, 1.00, 1.00, 0.780)),
]

hu_color_map = grayscale_hu_color_map if use_grayscale_color_palette else warm_hu_color_map

# Load DICOM series
dicom_loader = pv.DICOMLoader(dicom_path)
med.imaging.print_loaded_dicom_info(dicom_loader)

# Convert to volume and attribute
dicom_volume = dicom_loader.as_volume()
dicom_attribute = pv.FloatAttribute(dicom_volume)

object = pv.Mesh(mesh_path)
object.set_attribute(pv.DefaultAttributes.HU, dicom_attribute)

# Map HU to color
mod = pv.LookupTableConverter([pv.DefaultAttributes.HU], [pv.DefaultAttributes.COLOR_RGBA], hu_color_map, pv.InterpolationMode.LINEAR)
object = pv.AttributeModifier(mod, object)

if MAPPING_MODE == "mechanical":
    resolver.clear_conversions()
    resolver.register_j750_modulus_toughness_conversions(
        material_defs=materials,
        rigid_material=RIGID_MATERIAL,
        soft_material=SOFT_MATERIAL,
        liquid_material=LIQUID_MATERIAL,
    )

    # Map HU to modulus and toughness.
    prop_entries = [
        pv.LookupTableEntry(kv[0][0], kv[0][1], kv[1])
        for kv in hu_prop_map
    ]
    prop_mod = pv.LookupTableConverter(
        [pv.DefaultAttributes.HU],
        [pv.DefaultAttributes.MODULUS, pv.DefaultAttributes.TOUGHNESS],
        prop_entries,
        pv.InterpolationMode.STEP,
    )
    object = pv.AttributeModifier(prop_mod, object)

    # Map modulus and toughness to volume fractions.
    object = resolver.adapt(
        object,
        [pv.DefaultAttributes.VOLUME_FRACTIONS],
        tags=["j750_modulus_toughness"],
    )
else:
    # Map the contrast-windowed HU range directly across the full
    # VeroClear-to-RadioMatrix fraction range. LINEAR lookup clamps values
    # outside this robust histogram range to the nearest pure material.
    volume_fraction_entries = [
        pv.LookupTableEntry(
            VOLUME_FRACTION_HU_MIN,
            {
                materials.id(RADIO_MATRIX_MATERIAL): 0.0,
                materials.id(VERO_MATERIAL): 1.0,
            },
        ),
        pv.LookupTableEntry(
            VOLUME_FRACTION_HU_MAX,
            {
                materials.id(RADIO_MATRIX_MATERIAL): 1.0,
                materials.id(VERO_MATERIAL): 0.0,
            },
        ),
    ]
    volume_fraction_mod = pv.LookupTableConverter(
        [pv.DefaultAttributes.HU],
        [pv.DefaultAttributes.VOLUME_FRACTIONS],
        volume_fraction_entries,
        pv.InterpolationMode.LINEAR,
    )
    object = pv.AttributeModifier(volume_fraction_mod, object)

# Preserve the original print orientation, where the foot length is X.
object = pv.Rotate(0,0,90, object)
object = pv.Rotate(-17,-35,0, object)

# Measure the transformed foot and scale its X length to the scanner field of
# view before adding the mounting geometry.
bandwidth = max(voxel_size.x, voxel_size.y, voxel_size.z) * 6.0
object.prepare(voxel_size, bandwidth)
foot_bbox_min, foot_bbox_max = object.bounding_box()
foot_x_length = foot_bbox_max.x - foot_bbox_min.x
if foot_x_length <= 0.0:
    raise RuntimeError("Foot bounding box must have a positive X length.")

object = pv.Scale(FOOT_X_LENGTH / foot_x_length, object)
object.prepare(voxel_size, bandwidth)
foot_bbox_min, foot_bbox_max = object.bounding_box()
print(
    "Foot Model Size (mm): "
    f"{foot_bbox_max.x - foot_bbox_min.x:.2f} x "
    f"{foot_bbox_max.y - foot_bbox_min.y:.2f} x "
    f"{foot_bbox_max.z - foot_bbox_min.z:.2f}"
)

if ENABLE_MOUNTING_BAR:
    foot_x_length = foot_bbox_max.x - foot_bbox_min.x
    mounting_bar_extension = foot_x_length * MOUNTING_BAR_EXTENSION_RATIO
    mounting_bar_embedded_length = foot_x_length * MOUNTING_BAR_EMBEDDED_RATIO
    mounting_bar_cross_section = (
        FOOT_X_LENGTH * MOUNTING_BAR_CROSS_SECTION_RATIO
    )
    mounting_bar = pv.RectPrism.FromMinAndMax(
        pv.Vec3(
            foot_bbox_max.x - mounting_bar_embedded_length,
            (foot_bbox_min.y + foot_bbox_max.y) / 2.0
            - mounting_bar_cross_section / 2.0,
            (foot_bbox_min.z + foot_bbox_max.z) / 2.0
            - mounting_bar_cross_section / 2.0,
        ),
        pv.Vec3(
            foot_bbox_max.x + mounting_bar_extension,
            (foot_bbox_min.y + foot_bbox_max.y) / 2.0
            + mounting_bar_cross_section / 2.0,
            (foot_bbox_min.z + foot_bbox_max.z) / 2.0
            + mounting_bar_cross_section / 2.0,
        ),
    )
    mounting_bar.set_attribute(
        pv.DefaultAttributes.VOLUME_FRACTIONS,
        pv.VolumeFractionsAttribute([
            (1.0, materials.id(MOUNTING_MATERIAL)),
        ]),
    )
    # The foot precedes the bar so its mapped attributes win in the embedded
    # overlap, leaving the bar material only where it extends beyond the foot.
    object = pv.Union(0.0, [object, mounting_bar])
    object.prepare(voxel_size, bandwidth)

final_bbox_min, final_bbox_max = object.bounding_box()
print(
    "Final BBox Model Size (mm): "
    f"{final_bbox_max.x - final_bbox_min.x:.2f} x "
    f"{final_bbox_max.y - final_bbox_min.y:.2f} x "
    f"{final_bbox_max.z - final_bbox_min.z:.2f}"
)

if render:
    viz.Render(object, materials)

if export_material_inkjet or export_visual:
    import shutil, os

    def compile_output(compiler, output_dir, label):
        print(f"{label} Output Directory: {output_dir}")

        # Delete the output directory if it already exists
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)

        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)

        def print_progress(progress):
            print(f"{label} compilation progress: {progress*100:.2f}%")

        compiler.set_progress_callback(print_progress)
        compiler.compile()

    if export_material_inkjet:
        compiler = pvc.MaterialInkjetCompiler(object, voxel_size, material_output_dir, prefix, materials, liquid_keepout)
        compile_output(compiler, material_output_dir, "Material Inkjet")

    if export_visual:
        compiler = pvc.ColorInkjetCompiler(object, voxel_size, visual_output_dir, prefix)
        compile_output(compiler, visual_output_dir, "Visual")
