"""
RadioMatrix HU Gradient to Volume Fractions
===========================================

This example starts with a radiodensity design-intent field in Hounsfield
units, then uses the Stratasys RadioMatrix resolver module to synthesize
RadioMatrix/Vero/TissueMatrix material volume fractions for material inkjet.
"""
import os
import shutil

import pyvcad as pv
import pyvcad_attribute_resolver as resolver
import pyvcad_compilers as pvc
import pyvcad_rendering as viz
from pyvcad_attribute_resolver.modules.stratasys_radiomatrix import (
    MODE_RADIO_MATRIX_VERO_TISSUE_MATRIX,
    hu_anchors,
)

materials = pv.j750_materials

kv = 120  # Scanner voltage in kV. 100, 120, 140 are supported calibrations for now
mode = MODE_RADIO_MATRIX_VERO_TISSUE_MATRIX

BASE_BAR_LENGTH = 80.0
BASE_BAR_WIDTH = 18.0
BASE_BAR_HEIGHT = 10.0


def scaled_bar_size(target_x_length):
    scale = target_x_length / BASE_BAR_LENGTH
    return pv.Vec3(
        target_x_length,
        BASE_BAR_WIDTH * scale,
        BASE_BAR_HEIGHT * scale,
    )


SCANNER_PROFILES = [
    {
        "name": "cu_boulder_microct",
        "label": "CU Boulder MicroCT",
        "bar_size": scaled_bar_size(80.0),
        "scanner_notes": "Current example size and material-inkjet voxel size.",
    },
    {
        "name": "nist_microct",
        "label": "NIST MicroCT",
        "bar_size": scaled_bar_size(12.0),
        "scanner_notes": "Less than 25 mm on a side; 12 mm is ideal; 10-40 um scanner voxels.",
    },
    {
        "name": "nist_low_field_mri",
        "label": "NIST low-field MRI",
        "bar_size": scaled_bar_size(160.0),
        "scanner_notes": "Conservative size for 200 mm capacity; about 1 x 1 x 2 mm resolution.",
    },
    {
        "name": "three_t_mri",
        "label": "3T MRI",
        "bar_size": scaled_bar_size(80.0),
        "scanner_notes": "Conservative size for 100 mm diameter capacity; 0.25 mm voxel capability.",
    },
]

EXPORT_PROFILE_NAMES = ["nist_microct", "three_t_mri"]
RENDER_PROFILE_NAME = "nist_microct"
RUN_MATERIAL_INKJET_COMPILER = False
ENABLE_RENDER = True

# Optional overrides for non-interactive smoke checks.
if os.environ.get("OPENVCAD_EXPORT_PROFILES"):
    EXPORT_PROFILE_NAMES = [
        name.strip()
        for name in os.environ["OPENVCAD_EXPORT_PROFILES"].split(",")
        if name.strip()
    ]
if os.environ.get("OPENVCAD_RENDER_PROFILE"):
    RENDER_PROFILE_NAME = os.environ["OPENVCAD_RENDER_PROFILE"]
if os.environ.get("OPENVCAD_RUN_COMPILER") == "0":
    RUN_MATERIAL_INKJET_COMPILER = False
if os.environ.get("OPENVCAD_ENABLE_RENDER") == "0":
    ENABLE_RENDER = False

# Compiler controls. Output is ignored by git through this folder's .gitignore.
voxel_size = pv.Vec3(0.0423, 0.0846, 0.027)
output_root_dir = os.path.join(
    os.path.dirname(__file__),
    "output",
    "radiomatrix_hu_gradient",
)
prefix = "slice_"
liquid_keepout = 0.0


def scanner_profile(profile_name):
    for profile in SCANNER_PROFILES:
        if profile["name"] == profile_name:
            return profile
    raise RuntimeError("Unknown scanner profile: {}".format(profile_name))


def selected_export_profiles():
    return [scanner_profile(profile_name) for profile_name in EXPORT_PROFILE_NAMES]


def hu_targets():
    anchors = hu_anchors(kv, mode)
    hu_min = anchors["tissue_matrix"]
    hu_max = anchors["radio_matrix"]
    return hu_min, hu_max


def hu_gradient_expression(bar_length):
    hu_min, hu_max = hu_targets()
    hu_span = hu_max - hu_min
    return (
        "max(min(({span:.8f} * (x + {half_length:.8f}) / {length:.8f}) + "
        "{hu_min:.8f}, {hu_max:.8f}), {hu_min:.8f})"
    ).format(
        span=hu_span,
        half_length=bar_length / 2.0,
        length=bar_length,
        hu_min=hu_min,
        hu_max=hu_max,
    )


def build_unresolved_root(profile):
    bar_size = profile["bar_size"]
    bar = pv.RectPrism(
        pv.Vec3(0.0, 0.0, 0.0),
        bar_size,
    )
    bar.set_attribute(
        pv.DefaultAttributes.HU,
        pv.FloatAttribute(hu_gradient_expression(bar_size.x)),
    )
    return bar


def build_root(profile):
    root = build_unresolved_root(profile)
    resolver.clear_conversions()
    resolver.register_stratasys_radiomatrix_conversions(
        kv,
        material_defs=materials,
        mode=mode,
    )
    return resolver.adapt(
        root,
        [pv.DefaultAttributes.VOLUME_FRACTIONS],
        tags=[
            "stratasys_radiomatrix_{}kv".format(kv),
            "stratasys_radiomatrix_{}".format(mode),
        ],
    )


def prepared_bounding_box(root):
    bandwidth = max(voxel_size.x, voxel_size.y, voxel_size.z) * 6.0
    root.prepare(voxel_size, bandwidth)
    return root.bounding_box()


def format_size_value(value):
    rounded = round(value, 1)
    text = "{:.1f}".format(rounded).rstrip("0").rstrip(".")
    return text.replace(".", "p")


def size_slug_from_bbox(bbox_min, bbox_max):
    x_length = bbox_max.x - bbox_min.x
    y_length = bbox_max.y - bbox_min.y
    z_length = bbox_max.z - bbox_min.z
    return "{}x{}x{}mm".format(
        format_size_value(x_length),
        format_size_value(y_length),
        format_size_value(z_length),
    )


def format_vec3(vec):
    return "({:.4f}, {:.4f}, {:.4f})".format(vec.x, vec.y, vec.z)


def output_dir_for_profile(profile, bbox_min, bbox_max):
    return os.path.join(
        output_root_dir,
        "{}_{}".format(profile["name"], size_slug_from_bbox(bbox_min, bbox_max)),
    )


def print_profile_metadata(profile, bbox_min, bbox_max):
    x_length = bbox_max.x - bbox_min.x
    y_length = bbox_max.y - bbox_min.y
    z_length = bbox_max.z - bbox_min.z
    print("scanner profile:", profile["label"])
    print("  name:", profile["name"])
    print("  notes:", profile["scanner_notes"])
    print("  bbox min:", format_vec3(bbox_min))
    print("  bbox max:", format_vec3(bbox_max))
    print(
        "  final size: {:.4f} x {:.4f} x {:.4f} mm".format(
            x_length,
            y_length,
            z_length,
        )
    )


def on_progress(progress):
    print("compile progress: {:.1f}%".format(100.0 * progress))


def compile_profile(profile, root):
    bbox_min, bbox_max = prepared_bounding_box(root)
    output_dir = output_dir_for_profile(profile, bbox_min, bbox_max)
    print_profile_metadata(profile, bbox_min, bbox_max)

    if os.path.isdir(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    compiler = pvc.MaterialInkjetCompiler(
        root,
        voxel_size,
        output_dir,
        prefix,
        materials,
        liquid_keepout,
    )
    compiler.set_strict_mode(True)
    compiler.set_progress_callback(on_progress)
    compiler.compile()
    print("  output directory:", output_dir)
    print("  resolution (x, y, z png count):", compiler.resolution())
    print("  material voxel counts:", compiler.material_voxel_counts())


render_root = None

if RUN_MATERIAL_INKJET_COMPILER:
    for export_profile in selected_export_profiles():
        profile_root = build_root(export_profile)
        compile_profile(export_profile, profile_root)
        if export_profile["name"] == RENDER_PROFILE_NAME:
            render_root = profile_root

if ENABLE_RENDER:
    if render_root is None:
        render_root = build_root(scanner_profile(RENDER_PROFILE_NAME))
    viz.Render(render_root, materials)
