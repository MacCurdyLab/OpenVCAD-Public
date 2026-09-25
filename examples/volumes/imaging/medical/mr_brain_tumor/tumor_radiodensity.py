"""
Brain Tumor RadioMatrix/VeroBlack Phantom
==============================================

This example turns the segmented brain volume used by ``tumor.py`` into
a material-inkjet phantom. Intensity is windowed into a continuous
RadioMatrix/VeroBlack material mixture, with an optional offset shell that
masks exterior skin and bone from the material output.

Extract ``dicom.zip`` into a ``dicom/`` directory next to this file before
running the example.
"""
import os
import shutil

import pyvcad as pv
import pyvcad_compilers as pvc
import pyvcad_medical as med
import pyvcad_rendering as viz

materials = pv.j750_materials

# Select ``whole``, ``left``, or ``right``. Half-brain prints never include
# the mounting stick, even when ENABLE_MOUNTING_STICK is true.
MODE = "whole"
ENABLE_MOUNTING_STICK = True
# Masks exterior skin and bone from the material output. Disable this to
# preserve the source intensity all the way to the segmented surface.
ENABLE_OUTER_TISSUE_MASK = False
RENDER = True
EXPORT_MATERIAL_INKJET = True

voxel_size = pv.Vec3(0.0423, 0.0846, 0.027)

RADIO_MATRIX_MATERIAL = "RadioMatrix"
VERO_BLACK_MATERIAL = "VeroBlack"

# The current MR brain volume spans 0-695 after DICOM rescaling. These are
# the 75-190 display-window bounds from tumor.py, repurposed as the useful
# tissue-contrast range for the phantom material gradient. Values outside the
# window clamp to the nearest pure material.
INTENSITY_MIN = 75.0
INTENSITY_MAX = 190.0
OUTER_TISSUE_MASK_OFFSET = 11.0  # mm

# Match the ankle phantom's smallest scanner-oriented length. The brain is
# rotated first so its longest anatomical dimension is X, then uniformly
# scaled to this length before the stick is added.
BRAIN_X_LENGTH = 45.0  # mm
MOUNTING_STICK_EXTENSION_RATIO = 0.25
MOUNTING_STICK_EMBEDDED_RATIO = 0.08
MOUNTING_STICK_CROSS_SECTION_RATIO = 0.05

if MODE not in ("whole", "left", "right"):
    raise ValueError("MODE must be 'whole', 'left', or 'right'.")

script_dir = os.path.dirname(os.path.abspath(__file__))
dicom_path = os.path.join(script_dir, "dicom")
mesh_path = os.path.join(script_dir, "MRTumor.stl")
size_slug = "{:g}".format(BRAIN_X_LENGTH).replace(".", "p")
output_dir = os.path.join(
    script_dir,
    "output",
    "tumor_radiodensity_{}_x{}mm".format(MODE, size_slug),
)
prefix = "tumor_"

# Load the DICOM signal as the source scalar field and mask it with the
# existing segmented brain surface.
dicom_loader = pv.DICOMLoader(dicom_path)
med.imaging.print_loaded_dicom_info(dicom_loader)
dicom_attribute = pv.FloatAttribute(dicom_loader.as_volume())

# Map the contrast-windowed signal directly across the VeroBlack to
# RadioMatrix fraction range. LINEAR lookup clamps exterior intensities to
# the two pure material endpoints.
volume_fraction_entries = [
    pv.LookupTableEntry(
        INTENSITY_MIN,
        {
            materials.id(RADIO_MATRIX_MATERIAL): 0.0,
            materials.id(VERO_BLACK_MATERIAL): 1.0,
        },
    ),
    pv.LookupTableEntry(
        INTENSITY_MAX,
        {
            materials.id(RADIO_MATRIX_MATERIAL): 1.0,
            materials.id(VERO_BLACK_MATERIAL): 0.0,
        },
    ),
]
volume_fraction_mod = pv.LookupTableConverter(
    [pv.DefaultAttributes.HU],
    [pv.DefaultAttributes.VOLUME_FRACTIONS],
    volume_fraction_entries,
    pv.InterpolationMode.LINEAR,
)

if ENABLE_OUTER_TISSUE_MASK:
    # Match tumor.py's offset construction. The shell deliberately has no
    # VOLUME_FRACTIONS attribute, so MaterialInkjetCompiler emits it as void
    # while the contracted interior carries the material gradient.
    outer_brain = pv.Mesh(mesh_path)
    inner_source = pv.Offset(
        -OUTER_TISSUE_MASK_OFFSET,
        pv.Mesh(mesh_path),
    )
    inner_source.set_attribute(pv.DefaultAttributes.HU, dicom_attribute)
    inner_brain = pv.AttributeModifier(volume_fraction_mod, inner_source)
    outer_mask = pv.Difference(outer_brain, inner_source)
    brain = pv.Union(outer_mask, inner_brain)
else:
    brain = pv.Mesh(mesh_path)
    brain.set_attribute(pv.DefaultAttributes.HU, dicom_attribute)
    brain = pv.AttributeModifier(volume_fraction_mod, brain)

# The original tumor example defines hemispheres along the unrotated X axis.
if MODE != "whole":
    bandwidth = max(voxel_size.x, voxel_size.y, voxel_size.z) * 6.0
    brain.prepare(voxel_size, bandwidth)
    bbox_min, bbox_max = brain.bounding_box()
    x_size = (bbox_max.x - bbox_min.x) / 2.0
    clip_center_x = (bbox_min.x + bbox_max.x) / 2.0
    if MODE == "right":
        clip_center_x += x_size / 2.0
    else:
        clip_center_x -= x_size / 2.0
    hemisphere_clip = pv.RectPrism(
        pv.Vec3(
            clip_center_x,
            (bbox_min.y + bbox_max.y) / 2.0,
            (bbox_min.z + bbox_max.z) / 2.0,
        ),
        pv.Vec3(x_size, bbox_max.y - bbox_min.y, bbox_max.z - bbox_min.z),
    )
    brain = pv.Intersection(brain, hemisphere_clip)

# Preserve the print orientation used by the color brain model.
brain = pv.Rotate(0.0, 0.0, -90.0, brain)
bandwidth = max(voxel_size.x, voxel_size.y, voxel_size.z) * 6.0
brain.prepare(voxel_size, bandwidth)
brain_bbox_min, brain_bbox_max = brain.bounding_box()
brain_x_length = brain_bbox_max.x - brain_bbox_min.x
if brain_x_length <= 0.0:
    raise RuntimeError("Brain bounding box must have a positive X length.")

brain = pv.Scale(BRAIN_X_LENGTH / brain_x_length, brain)
brain.prepare(voxel_size, bandwidth)
brain_bbox_min, brain_bbox_max = brain.bounding_box()
print(
    "Brain Model Size (mm): "
    f"{brain_bbox_max.x - brain_bbox_min.x:.2f} x "
    f"{brain_bbox_max.y - brain_bbox_min.y:.2f} x "
    f"{brain_bbox_max.z - brain_bbox_min.z:.2f}"
)

root = brain
if MODE == "whole" and ENABLE_MOUNTING_STICK:
    mounting_stick_extension = BRAIN_X_LENGTH * MOUNTING_STICK_EXTENSION_RATIO
    mounting_stick_embedded_length = (
        BRAIN_X_LENGTH * MOUNTING_STICK_EMBEDDED_RATIO
    )
    mounting_stick_cross_section = (
        BRAIN_X_LENGTH * MOUNTING_STICK_CROSS_SECTION_RATIO
    )
    mounting_stick = pv.RectPrism.FromMinAndMax(
        pv.Vec3(
            brain_bbox_min.x - mounting_stick_extension,
            (brain_bbox_min.y + brain_bbox_max.y) / 2.0
            - mounting_stick_cross_section / 2.0,
            (brain_bbox_min.z + brain_bbox_max.z) / 2.0
            - mounting_stick_cross_section / 2.0,
        ),
        pv.Vec3(
            brain_bbox_min.x + mounting_stick_embedded_length,
            (brain_bbox_min.y + brain_bbox_max.y) / 2.0
            + mounting_stick_cross_section / 2.0,
            (brain_bbox_min.z + brain_bbox_max.z) / 2.0
            + mounting_stick_cross_section / 2.0,
        ),
    )
    mounting_stick.set_attribute(
        pv.DefaultAttributes.VOLUME_FRACTIONS,
        pv.VolumeFractionsAttribute([
            (1.0, materials.id(VERO_BLACK_MATERIAL)),
        ]),
    )
    # The brain precedes the stick so its material mapping wins in the
    # embedded overlap; the exposed posterior extension is pure VeroBlack.
    root = pv.Union(0.0, [brain, mounting_stick])

root.prepare(voxel_size, bandwidth)
final_bbox_min, final_bbox_max = root.bounding_box()
print(
    "Final Model Size (mm): "
    f"{final_bbox_max.x - final_bbox_min.x:.2f} x "
    f"{final_bbox_max.y - final_bbox_min.y:.2f} x "
    f"{final_bbox_max.z - final_bbox_min.z:.2f}"
)

if RENDER:
    viz.Render(root, materials)

if EXPORT_MATERIAL_INKJET:
    print(f"Material Inkjet Output Directory: {output_dir}")
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    compiler = pvc.MaterialInkjetCompiler(
        root,
        voxel_size,
        output_dir,
        prefix,
        materials
    )
    compiler.set_fallback_material_id(materials.id("void"))

    def print_progress(progress):
        print(f"Material Inkjet compilation progress: {progress*100:.2f}%")

    compiler.set_progress_callback(print_progress)
    compiler.compile()
