"""
RadioMatrix HU QR Code
======================

This example adapts the OpenVCAD QR code badge to use HU design targets.
The Stratasys RadioMatrix resolver converts those HU targets into VeroBlack
and RadioMatrix volume fractions. A labeled VeroPureWht clamp tab is then
added in volume-fraction space before the complete assembly is uniformly
scaled.
"""
import os
import shutil

import pyvcad as pv
import pyvcad_attribute_resolver as resolver
import pyvcad_compilers as pvc
import pyvcad_rendering as viz
from pyvcad_attribute_resolver.modules.stratasys_radiomatrix import (
    MODE_RADIO_MATRIX_VERO,
    hu_anchors,
)

materials = pv.j750_materials

# RadioMatrix/Vero-only calibration controls.
kv = 140
mode = MODE_RADIO_MATRIX_VERO
RADIO_MATRIX_MATERIAL = "RadioMatrix"
VERO_BLACK_MATERIAL = "VeroBlack"
CONTRAST_MATERIAL = "VeroPureWht"

# Final CU scanner dimensions. The clamp tab is additional to the desired
# scanned-object length and preserves the badge width and height.
DESIRED_OBJECT_X_LENGTH = 80.0
DEAD_ZONE_X_PERCENTAGE = 10.0
use_gyroid_fill = True
USE_ERROR_DIFFUSION = True

RUN_MATERIAL_INKJET_COMPILER = False
ENABLE_RENDER = True


if USE_ERROR_DIFFUSION:
    EXPORT_MODE = pvc.MaterialInkjetExportMode.DITHERED_3D
    EXPORT_MODE_SLUG = "error_diffusion"
    EXPORT_MODE_LABEL = "ERROR DIFFUSION"
else:
    EXPORT_MODE = pvc.MaterialInkjetExportMode.STOCHASTIC
    EXPORT_MODE_SLUG = "stochastic"
    EXPORT_MODE_LABEL = "STOCHASTIC"

# Optional overrides for non-interactive smoke checks.
if os.environ.get("OPENVCAD_RUN_COMPILER") == "0":
    RUN_MATERIAL_INKJET_COMPILER = False
if os.environ.get("OPENVCAD_ENABLE_RENDER") == "0":
    ENABLE_RENDER = False

# Shared paths and mesh loading controls.
data_dir = os.path.join(
    os.path.dirname(__file__),
    "..",
    "..",
    "data",
    "3d_models",
)
qr_base_file = "qr_code_base.3mf"
qr_code_file = "qr_code_code.3mf"
qr_border_file = "qr_code_border.3mf"
mesh_center = False
mesh_disable_validation = True

# Source geometry controls from the original QR code example.
source_bar_center = pv.Vec3(0.0, 0.0, 0.0)
source_bar_size = pv.Vec3(173.0, 32.0, 12.0)

qr_scale = 1.0
qr_translation = pv.Vec3(-69.0, 0.0, -1.5)

text_string = "OpenVCAD"
text_height = 26.5
text_depth = 5.6
text_font = "Arial"
text_aspect = pv.FontAspect.Regular
text_horizontal_alignment = pv.HorizontalAlignment.Center
text_vertical_alignment = pv.VerticalAlignment.Center
text_scale = 1.0
text_rotation_pitch = 0.0
text_rotation_yaw = 0.0
text_rotation_roll = 180.0
text_translation = pv.Vec3(14.5, -1.75, 0.0)
text_gradient_width = 136.0

CLAMP_LABEL_PADDING_FRACTION = 0.1
CLAMP_LABEL_DEPTH_FRACTION = 0.08
CLAMP_LABEL_FONT = "Arial"

gyroid_frequency_scale = 1.1
gyroid_period = 1.0
gyroid_offset = 0.5
gyroid_min = pv.Vec3(-72.0, -18.0, -6.0)
gyroid_max = pv.Vec3(72.0, 18.0, 6.0)

# Compiler controls. Output is ignored by git through this folder's .gitignore.
voxel_size = pv.Vec3(0.0423, 0.0846, 0.027)
output_root_dir = os.path.join(
    os.path.dirname(__file__),
    "output",
)
prefix = "slice_"
liquid_keepout = 0.0


def data_path(filename):
    return os.path.join(data_dir, filename)


def hu_targets():
    anchors = hu_anchors(kv, mode)
    hu_min = anchors["vero"]
    hu_max = anchors["radio_matrix"]
    hu_span = hu_max - hu_min
    return {
        "background": hu_min,
        "qr_background": hu_min + 0.35 * hu_span,
        "qr_code": hu_max,
        "text_high": hu_max,
        "text_low": hu_min + 0.20 * hu_span,
    }


def set_hu(node, hu):
    node.set_attribute(
        pv.DefaultAttributes.HU,
        pv.FloatAttribute(float(hu)),
    )
    return node


def set_uniform_material(node, material_name):
    node.set_attribute(
        pv.DefaultAttributes.VOLUME_FRACTIONS,
        pv.VolumeFractionsAttribute([(1.0, materials.id(material_name))]),
    )
    return node


def load_qr_mesh(filename, hu):
    mesh = pv.Mesh(
        data_path(filename),
        mesh_center,
        mesh_disable_validation,
    )
    return set_hu(mesh, hu)


def text_hu_gradient_expression(text_high_hu, text_low_hu):
    half_width = text_gradient_width / 2.0
    return (
        "{high:.8f} + ({low:.8f} - {high:.8f}) * "
        "max(min((x + {half_width:.8f}) / {width:.8f}, 1.0), 0.0)"
    ).format(
        high=text_high_hu,
        low=text_low_hu,
        half_width=half_width,
        width=text_gradient_width,
    )


def bounding_box(node):
    node.prepare(pv.Vec3(1.0, 1.0, 1.0), 1.0)
    return node.bounding_box()


def build_qr_code(targets):
    qr_base = load_qr_mesh(qr_base_file, targets["qr_background"])
    qr_code = load_qr_mesh(qr_code_file, targets["qr_code"])
    qr_border = load_qr_mesh(qr_border_file, targets["qr_code"])
    qr_code_combined = pv.Union(0.0, [qr_base, qr_code, qr_border])
    qr_code_combined = pv.Scale(qr_scale, qr_code_combined)
    return pv.Translate(
        qr_translation.x,
        qr_translation.y,
        qr_translation.z,
        qr_code_combined,
    )


def build_text(targets):
    openvcad_text = pv.Text(
        text_string,
        text_height,
        text_depth,
        text_aspect,
        text_font,
        text_horizontal_alignment,
        text_vertical_alignment,
    )
    openvcad_text.set_attribute(
        pv.DefaultAttributes.HU,
        pv.FloatAttribute(
            text_hu_gradient_expression(
                targets["text_high"],
                targets["text_low"],
            )
        ),
    )

    if use_gyroid_fill:
        gyroid_expression = (
            "sin(({frequency} * pi * x) / {period}) * "
            "cos(({frequency} * pi * y) / {period}) + "
            "sin(({frequency} * pi * y) / {period}) * "
            "cos(({frequency} * pi * z) / {period}) + "
            "sin(({frequency} * pi * z) / {period}) * "
            "cos(({frequency} * pi * x) / {period}) + "
            "{offset}"
        ).format(
            frequency=gyroid_frequency_scale,
            period=gyroid_period,
            offset=gyroid_offset,
        )
        gyroid = pv.Function(gyroid_expression, gyroid_min, gyroid_max)
        text_node = pv.Intersection(0.0, [openvcad_text, gyroid])
    else:
        text_node = openvcad_text

    text_node = pv.Scale(text_scale, text_node)
    text_node = pv.Rotate(
        text_rotation_pitch,
        text_rotation_yaw,
        text_rotation_roll,
        text_node,
    )
    return pv.Translate(
        text_translation.x,
        text_translation.y,
        text_translation.z,
        text_node,
    )


def build_unresolved_root():
    targets = hu_targets()
    qr_code_combined = build_qr_code(targets)
    text_node = build_text(targets)
    bar = pv.RectPrism(source_bar_center, source_bar_size)
    bar = set_hu(bar, targets["background"])

    # Child order is intentional: feature HU attributes win over the background
    # bar in overlaps.
    return pv.Union(0.0, [qr_code_combined, text_node, bar])


def clamp_label_texts():
    gyroid_label = "GYROID" if use_gyroid_fill else "NO GYROID"
    diffusion_label = "DITHERED" if USE_ERROR_DIFFUSION else "NOT DITHERED"
    return gyroid_label, diffusion_label


def make_clamp_label_text(text, height, depth):
    label = pv.Text(
        text,
        height,
        depth,
        pv.FontAspect.Bold,
        CLAMP_LABEL_FONT,
        pv.HorizontalAlignment.Center,
        pv.VerticalAlignment.Center,
    )
    return pv.Rotate(0.0, 0.0, 90.0, label)


def clamp_label_dimensions(
    labels,
    clamp_x_length,
    object_y_length,
    object_z_length,
):
    lane_x_length = clamp_x_length / len(labels)
    padding_scale = 1.0 - 2.0 * CLAMP_LABEL_PADDING_FRACTION
    available_x_length = lane_x_length * padding_scale
    available_y_length = object_y_length * padding_scale

    unit_sizes = []
    for text in labels:
        unit_label = make_clamp_label_text(text, 1.0, 1.0)
        unit_min, unit_max = bounding_box(unit_label)
        unit_sizes.append(
            (
                unit_max.x - unit_min.x,
                unit_max.y - unit_min.y,
            )
        )

    max_unit_x_length = max(size[0] for size in unit_sizes)
    max_unit_y_length = max(size[1] for size in unit_sizes)
    label_height = min(
        available_x_length / max_unit_x_length,
        available_y_length / max_unit_y_length,
    )
    label_depth = object_z_length * CLAMP_LABEL_DEPTH_FRACTION
    return label_height, label_depth


def make_clamp_label_shape(text, x, y, z, height, depth):
    label = make_clamp_label_text(text, height, depth)
    return pv.Translate(x, y, z, label)


def build_clamping_region(
    bbox_min,
    bbox_max,
    contrast_material_name,
    label_material_name,
):
    object_x_length = bbox_max.x - bbox_min.x
    object_y_length = bbox_max.y - bbox_min.y
    object_z_length = bbox_max.z - bbox_min.z
    dead_zone_x_length = object_x_length * DEAD_ZONE_X_PERCENTAGE / 100.0
    dead_zone_center = pv.Vec3(
        bbox_max.x + dead_zone_x_length / 2.0,
        (bbox_min.y + bbox_max.y) / 2.0,
        (bbox_min.z + bbox_max.z) / 2.0,
    )
    clamping_region = pv.RectPrism(
        dead_zone_center,
        pv.Vec3(dead_zone_x_length, object_y_length, object_z_length),
    )
    set_uniform_material(clamping_region, contrast_material_name)

    labels = clamp_label_texts()
    label_height, label_depth = clamp_label_dimensions(
        labels,
        dead_zone_x_length,
        object_y_length,
        object_z_length,
    )
    label_z = bbox_max.z - label_depth / 2.0
    label_x_positions = (
        dead_zone_center.x - dead_zone_x_length / 4.0,
        dead_zone_center.x + dead_zone_x_length / 4.0,
    )
    label_y = dead_zone_center.y

    cutouts = [
        make_clamp_label_shape(
            text,
            x,
            label_y,
            label_z,
            label_height,
            label_depth,
        )
        for text, x in zip(labels, label_x_positions)
    ]
    label_fills = [
        set_uniform_material(
            make_clamp_label_shape(
                text,
                x,
                label_y,
                label_z,
                label_height,
                label_depth,
            ),
            label_material_name,
        )
        for text, x in zip(labels, label_x_positions)
    ]

    carved_region = pv.Difference(
        clamping_region,
        pv.Union(0.0, cutouts),
    )
    # Label fills precede the clamp so their material wins on shared faces.
    return pv.Union(0.0, label_fills + [carved_region])


def build_root(
    radio_matrix_name=RADIO_MATRIX_MATERIAL,
    vero_name=VERO_BLACK_MATERIAL,
    contrast_material_name=CONTRAST_MATERIAL,
    label_material_name=VERO_BLACK_MATERIAL,
):
    unresolved_root = build_unresolved_root()
    bbox_min, bbox_max = bounding_box(unresolved_root)
    source_object_x_length = bbox_max.x - bbox_min.x
    if source_object_x_length <= 0.0:
        raise RuntimeError("Cannot scale a node with non-positive x length.")

    resolver.clear_conversions()
    resolver.register_stratasys_radiomatrix_conversions(
        kv,
        material_defs=materials,
        radio_matrix_material=radio_matrix_name,
        vero_material=vero_name,
        mode=mode,
    )
    resolved_root = resolver.adapt(
        unresolved_root,
        [pv.DefaultAttributes.VOLUME_FRACTIONS],
        tags=[
            "stratasys_radiomatrix_{}kv".format(kv),
            "stratasys_radiomatrix_{}".format(mode),
        ],
    )
    scale = DESIRED_OBJECT_X_LENGTH / source_object_x_length
    clamping_region = build_clamping_region(
        bbox_min,
        bbox_max,
        contrast_material_name,
        label_material_name,
    )
    assembled_root = pv.Union(0.0, [resolved_root, clamping_region])
    return pv.Scale(scale, assembled_root)


def prepared_bounding_box(root):
    bandwidth = max(voxel_size.x, voxel_size.y, voxel_size.z) * 6.0
    root.prepare(voxel_size, bandwidth)
    return root.bounding_box()


def format_size_value(value):
    rounded = round(value, 1)
    text = "{:.1f}".format(rounded).rstrip("0").rstrip(".")
    return text.replace(".", "p")


def object_length_slug():
    return "x{}mm".format(format_size_value(DESIRED_OBJECT_X_LENGTH))


def gyroid_slug():
    return "gyroid" if use_gyroid_fill else "no_gyroid"


def format_vec3(vec):
    return "({:.4f}, {:.4f}, {:.4f})".format(vec.x, vec.y, vec.z)


def output_dir_for_root():
    return os.path.join(
        output_root_dir,
        "radiomatrix_hu_qr_code_{}_{}_{}".format(
            object_length_slug(),
            EXPORT_MODE_SLUG,
            gyroid_slug(),
        ),
    )


def print_model_metadata(bbox_min, bbox_max):
    x_length = bbox_max.x - bbox_min.x
    y_length = bbox_max.y - bbox_min.y
    z_length = bbox_max.z - bbox_min.z
    print("design: RadioMatrix HU QR code")
    print("  material assignment mode:", EXPORT_MODE_LABEL)
    print("  gyroid fill:", "enabled" if use_gyroid_fill else "disabled")
    print("  clamp labels:", ", ".join(clamp_label_texts()))
    print("  modeled materials: {}, {}".format(
        RADIO_MATRIX_MATERIAL,
        VERO_BLACK_MATERIAL,
    ))
    print("  contrast material:", CONTRAST_MATERIAL)
    print("  desired object x length: {:.4f} mm".format(
        DESIRED_OBJECT_X_LENGTH
    ))
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


def compile_root(root):
    bbox_min, bbox_max = prepared_bounding_box(root)
    output_dir = output_dir_for_root()
    print_model_metadata(bbox_min, bbox_max)

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
        EXPORT_MODE,
    )
    compiler.set_strict_mode(True)
    compiler.set_progress_callback(on_progress)
    compiler.compile()
    print("  output directory:", output_dir)
    print("  resolution (x, y, z png count):", compiler.resolution())
    print("  material voxel counts:", compiler.material_voxel_counts())


root = build_root()

if ENABLE_RENDER:
    viz.Render(root, materials)

if RUN_MATERIAL_INKJET_COMPILER:
    compile_root(root)
