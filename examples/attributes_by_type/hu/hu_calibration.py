"""
RadioMatrix / VeroBlack CT HU Calibration Phantom
==================================================

Builds a compact J750 / PolyJet calibration object containing discrete
RadioMatrix/VeroBlack mixture swatches and a continuous 0-100% gradient.
The test regions are separated by a void divider that blocks error diffusion,
and the perimeter includes paired radiopaque and visible orientation markers.
Set USE_ERROR_DIFFUSION to choose the material assignment mode used for both
the exported PNG stack and the mode label inset into the object.
"""
import math
import os
import shutil

import pyvcad as pv
import pyvcad_compilers as pvc
import pyvcad_rendering as viz

materials = pv.j750_materials

ROWS = 3
COLS = 7

BASE_FINISHED_X_LENGTH = 45.0
BASE_BORDER_WIDTH = 3.0
BASE_TEST_X_LENGTH = BASE_FINISHED_X_LENGTH - 2.0 * BASE_BORDER_WIDTH
BASE_SWATCH_GRID_Y_WIDTH = 13.2
BASE_GRADIENT_Y_HEIGHT = BASE_SWATCH_GRID_Y_WIDTH / ROWS
# At the default 45 mm size, this is 5.91 native Y voxels. The current
# error-diffusion kernel reaches only one neighboring voxel along Y.
BASE_DIFFUSION_DIVIDER_Y_WIDTH = 0.5
BASE_TEST_Y_WIDTH = (
    BASE_SWATCH_GRID_Y_WIDTH
    + BASE_DIFFUSION_DIVIDER_Y_WIDTH
    + BASE_GRADIENT_Y_HEIGHT
)
BASE_FINISHED_Y_WIDTH = BASE_TEST_Y_WIDTH + 2.0 * BASE_BORDER_WIDTH
BASE_SAMPLE_THICKNESS_Z = 5.5

BASE_TEXT_DEPTH = 0.45
BASE_BORDER_EXTENSION_Z = 0.7
BASE_LABEL_LEFT_X = -10.5
BASE_LABEL_RIGHT_X = 11.0
BASE_LABEL_Y = 10.4
BASE_MODE_LABEL_X = 0.0
BASE_MODE_LABEL_Y = -BASE_LABEL_Y
BASE_LABEL_TEXT_HEIGHT = 1.8

BASE_MARKER_INSET = BASE_BORDER_WIDTH / 2.0
BASE_MARKER_SIZE = BASE_BORDER_WIDTH * 0.75
BASE_CROSS_ARM_WIDTH = BASE_MARKER_SIZE / 3.0

DIMENSION_TOLERANCE = 1e-5
FRACTION_TOLERANCE = 1e-6

# Change this finished X length to scale the complete design uniformly.
DESIRED_X_LENGTH = 100
RUN_MATERIAL_INKJET_COMPILER = True
ENABLE_RENDER = False

# Toggle between deterministic 3D error diffusion and stochastic assignment.
USE_ERROR_DIFFUSION = False

if USE_ERROR_DIFFUSION:
    EXPORT_MODE = pvc.MaterialInkjetExportMode.DITHERED_3D
    EXPORT_MODE_SLUG = "error_diffusion"
    EXPORT_MODE_LABEL = "MODE: ERROR DIFFUSION"
else:
    EXPORT_MODE = pvc.MaterialInkjetExportMode.STOCHASTIC
    EXPORT_MODE_SLUG = "stochastic"
    EXPORT_MODE_LABEL = "MODE: STOCHASTIC"

voxel_size = pv.Vec3(0.0423, 0.0846, 0.027)
output_root_dir = os.path.join(
    os.path.dirname(__file__),
    "output",
)
prefix = "slice_"
liquid_keepout = 0.0

RADIO_MATRIX_MATERIAL = "RadioMatrix"
VERO_BLACK_MATERIAL = "VeroBlack"
LABEL_MATERIAL = "VeroPureWht"

LEVEL_GRID = [
    [0, 5, 10, 15, 20, 25, 30],
    [35, 40, 45, 50, 55, 60, 65],
    [70, 75, 80, 85, 90, 95, 100],
]

radio_matrix_id = materials.id(RADIO_MATRIX_MATERIAL)
vero_black_id = materials.id(VERO_BLACK_MATERIAL)
label_material_id = materials.id(LABEL_MATERIAL)


def uniform_volume_fractions(entries):
    return pv.VolumeFractionsAttribute(
        [(float(value), material_id) for value, material_id in entries]
    )


def set_uniform_material(node, material_id):
    node.set_attribute(
        pv.DefaultAttributes.VOLUME_FRACTIONS,
        uniform_volume_fractions([(1.0, material_id)]),
    )
    return node


def design_values():
    block_x = BASE_TEST_X_LENGTH / COLS
    block_y = BASE_SWATCH_GRID_Y_WIDTH / ROWS
    test_x_min = -BASE_TEST_X_LENGTH / 2.0
    test_x_max = BASE_TEST_X_LENGTH / 2.0
    test_y_min = -BASE_TEST_Y_WIDTH / 2.0
    test_y_max = BASE_TEST_Y_WIDTH / 2.0
    gradient_y_min = test_y_min
    gradient_y_max = gradient_y_min + BASE_GRADIENT_Y_HEIGHT
    divider_y_min = gradient_y_max
    divider_y_max = divider_y_min + BASE_DIFFUSION_DIVIDER_Y_WIDTH
    swatch_y_min = divider_y_max
    swatch_y_max = test_y_max
    outer_x_min = -BASE_FINISHED_X_LENGTH / 2.0
    outer_x_max = BASE_FINISHED_X_LENGTH / 2.0
    outer_y_min = -BASE_FINISHED_Y_WIDTH / 2.0
    outer_y_max = BASE_FINISHED_Y_WIDTH / 2.0
    top_z = BASE_SAMPLE_THICKNESS_Z / 2.0
    return {
        "block_x": block_x,
        "block_y": block_y,
        "test_x_min": test_x_min,
        "test_x_max": test_x_max,
        "test_y_min": test_y_min,
        "test_y_max": test_y_max,
        "gradient_y_min": gradient_y_min,
        "gradient_y_max": gradient_y_max,
        "divider_y_min": divider_y_min,
        "divider_y_max": divider_y_max,
        "swatch_y_min": swatch_y_min,
        "swatch_y_max": swatch_y_max,
        "outer_x_min": outer_x_min,
        "outer_x_max": outer_x_max,
        "outer_y_min": outer_y_min,
        "outer_y_max": outer_y_max,
        "top_z": top_z,
    }


def make_sample_block(row, col, percent_radio_matrix, design):
    x_center = design["test_x_min"] + (col + 0.5) * design["block_x"]
    y_center = design["swatch_y_max"] - (row + 0.5) * design["block_y"]
    radio_matrix_fraction = percent_radio_matrix / 100.0
    vero_black_fraction = 1.0 - radio_matrix_fraction

    block = pv.RectPrism(
        pv.Vec3(x_center, y_center, 0.0),
        pv.Vec3(
            design["block_x"],
            design["block_y"],
            BASE_SAMPLE_THICKNESS_Z,
        ),
    )
    block.set_attribute(
        pv.DefaultAttributes.VOLUME_FRACTIONS,
        uniform_volume_fractions(
            [
                (radio_matrix_fraction, radio_matrix_id),
                (vero_black_fraction, vero_black_id),
            ]
        ),
    )

    x_min = design["test_x_min"] + col * design["block_x"]
    x_max = x_min + design["block_x"]
    y_max = design["swatch_y_max"] - row * design["block_y"]
    y_min = y_max - design["block_y"]

    sample_record = {
        "index": row * COLS + col + 1,
        "row": row + 1,
        "col": col + 1,
        "percent": percent_radio_matrix,
        "center": (x_center, y_center, 0.0),
        "x_bounds": (x_min, x_max),
        "y_bounds": (y_min, y_max),
        "z_bounds": (-design["top_z"], design["top_z"]),
    }
    return block, sample_record


def radio_matrix_gradient_expression(design):
    return (
        "max(min((x - ({x_min:.8f})) / {length:.8f}, 1.0), 0.0)"
    ).format(
        x_min=design["test_x_min"],
        length=BASE_TEST_X_LENGTH,
    )


def make_gradient_block(design):
    gradient_center_y = (
        design["gradient_y_min"] + design["gradient_y_max"]
    ) / 2.0
    radio_expression = radio_matrix_gradient_expression(design)
    gradient_attribute = pv.VolumeFractionsAttribute(
        [
            (radio_expression, radio_matrix_id),
            ("1.0 - ({})".format(radio_expression), vero_black_id),
        ]
    )
    gradient = pv.RectPrism(
        pv.Vec3(0.0, gradient_center_y, 0.0),
        pv.Vec3(
            BASE_TEST_X_LENGTH,
            BASE_GRADIENT_Y_HEIGHT,
            BASE_SAMPLE_THICKNESS_Z,
        ),
    )
    gradient.set_attribute(
        pv.DefaultAttributes.VOLUME_FRACTIONS,
        gradient_attribute,
    )
    return gradient, {
        "center": (0.0, gradient_center_y, 0.0),
        "x_bounds": (design["test_x_min"], design["test_x_max"]),
        "y_bounds": (design["gradient_y_min"], design["gradient_y_max"]),
        "z_bounds": (-design["top_z"], design["top_z"]),
        "attribute": gradient_attribute,
    }


def make_marker_shape(shape, x, y, z_center, height):
    half_size = BASE_MARKER_SIZE / 2.0
    if shape == "circle":
        return pv.Cylinder(
            pv.Vec3(x, y, z_center),
            half_size,
            height,
        )
    if shape == "triangle":
        vertices = [
            pv.Vec3(x, y + half_size, z_center),
            pv.Vec3(x - half_size, y - half_size, z_center),
            pv.Vec3(x + half_size, y - half_size, z_center),
        ]
        return pv.PolygonExtrude(vertices, height, True)
    if shape == "square":
        return pv.RectPrism(
            pv.Vec3(x, y, z_center),
            pv.Vec3(BASE_MARKER_SIZE, BASE_MARKER_SIZE, height),
        )
    if shape == "cross":
        horizontal = pv.RectPrism(
            pv.Vec3(x, y, z_center),
            pv.Vec3(BASE_MARKER_SIZE, BASE_CROSS_ARM_WIDTH, height),
        )
        vertical = pv.RectPrism(
            pv.Vec3(x, y, z_center),
            pv.Vec3(BASE_CROSS_ARM_WIDTH, BASE_MARKER_SIZE, height),
        )
        return pv.Union(0.0, [horizontal, vertical])
    raise RuntimeError("Unknown orientation marker shape: {}".format(shape))


def marker_layout(design):
    left_x = design["outer_x_min"] + BASE_MARKER_INSET
    right_x = design["outer_x_max"] - BASE_MARKER_INSET
    bottom_y = design["outer_y_min"] + BASE_MARKER_INSET
    top_y = design["outer_y_max"] - BASE_MARKER_INSET
    return [
        ("top-left", "circle", left_x, top_y),
        ("top-right", "triangle", right_x, top_y),
        ("bottom-right", "square", right_x, bottom_y),
        ("bottom-left", "cross", left_x, bottom_y),
    ]


def make_text_shape(text, x, design, y=BASE_LABEL_Y):
    text_node = pv.Text(
        text,
        BASE_LABEL_TEXT_HEIGHT,
        BASE_TEXT_DEPTH,
        pv.FontAspect.Bold,
        "Arial",
        pv.HorizontalAlignment.Center,
        pv.VerticalAlignment.Center,
    )
    text_node = pv.Rotate(0.0, 0.0, 180.0, text_node)
    return pv.Translate(
        x,
        y,
        (
            design["top_z"]
            + BASE_BORDER_EXTENSION_Z
            - BASE_TEXT_DEPTH / 2.0
        ),
        text_node,
    )


def make_inset_text(text, x, design, y=BASE_LABEL_Y):
    return set_uniform_material(
        make_text_shape(text, x, design, y),
        label_material_id,
    )


def make_frame_and_markers(design):
    frame_height = BASE_SAMPLE_THICKNESS_Z + BASE_BORDER_EXTENSION_Z
    frame_center_z = BASE_BORDER_EXTENSION_Z / 2.0
    horizontal_bar_center_y = (
        design["test_y_max"] + design["outer_y_max"]
    ) / 2.0
    vertical_bar_center_x = (
        design["test_x_max"] + design["outer_x_max"]
    ) / 2.0
    frame_bars = [
        pv.RectPrism(
            pv.Vec3(0.0, horizontal_bar_center_y, frame_center_z),
            pv.Vec3(
                BASE_FINISHED_X_LENGTH,
                BASE_BORDER_WIDTH,
                frame_height,
            ),
        ),
        pv.RectPrism(
            pv.Vec3(0.0, -horizontal_bar_center_y, frame_center_z),
            pv.Vec3(
                BASE_FINISHED_X_LENGTH,
                BASE_BORDER_WIDTH,
                frame_height,
            ),
        ),
        pv.RectPrism(
            pv.Vec3(vertical_bar_center_x, 0.0, frame_center_z),
            pv.Vec3(
                BASE_BORDER_WIDTH,
                BASE_TEST_Y_WIDTH,
                frame_height,
            ),
        ),
        pv.RectPrism(
            pv.Vec3(-vertical_bar_center_x, 0.0, frame_center_z),
            pv.Vec3(
                BASE_BORDER_WIDTH,
                BASE_TEST_Y_WIDTH,
                frame_height,
            ),
        ),
    ]
    cutouts = []
    in_plane_markers = []
    inset_markers = []
    marker_records = []

    for corner, shape, x, y in marker_layout(design):
        cutouts.append(
            make_marker_shape(shape, x, y, frame_center_z, frame_height)
        )

        in_plane_marker = make_marker_shape(
            shape,
            x,
            y,
            0.0,
            BASE_SAMPLE_THICKNESS_Z,
        )
        in_plane_markers.append(
            set_uniform_material(in_plane_marker, radio_matrix_id)
        )

        inset_center_z = design["top_z"] + BASE_BORDER_EXTENSION_Z / 2.0
        inset_marker = make_marker_shape(
            shape,
            x,
            y,
            inset_center_z,
            BASE_BORDER_EXTENSION_Z,
        )
        inset_markers.append(
            set_uniform_material(inset_marker, label_material_id)
        )

        marker_records.append(
            {
                "corner": corner,
                "shape": shape,
                "center": (x, y),
                "in_plane_z_bounds": (-design["top_z"], design["top_z"]),
                "inset_z_bounds": (
                    design["top_z"],
                    design["top_z"] + BASE_BORDER_EXTENSION_Z,
                ),
            }
        )

    cutouts.append(make_text_shape("RM/VeroBlack+", BASE_LABEL_LEFT_X, design))
    cutouts.append(make_text_shape("0-100% RM", BASE_LABEL_RIGHT_X, design))
    cutouts.append(
        make_text_shape(
            EXPORT_MODE_LABEL,
            BASE_MODE_LABEL_X,
            design,
            BASE_MODE_LABEL_Y,
        )
    )

    frame = pv.Difference(
        pv.Union(0.0, frame_bars),
        pv.Union(0.0, cutouts),
    )
    set_uniform_material(frame, vero_black_id)
    return frame, in_plane_markers, inset_markers, marker_records


def build_unscaled_root():
    design = design_values()
    children = []
    sample_records = []

    frame, in_plane_markers, inset_markers, marker_records = (
        make_frame_and_markers(design)
    )
    for row in range(ROWS):
        for col in range(COLS):
            sample_block, sample_record = make_sample_block(
                row,
                col,
                LEVEL_GRID[row][col],
                design,
            )
            children.append(sample_block)
            sample_records.append(sample_record)

    gradient, gradient_record = make_gradient_block(design)
    children.append(gradient)
    # Marker fills precede the frame so their attributes win on shared cut faces.
    children.extend(in_plane_markers)
    children.append(make_inset_text("RM/VeroBlack+", BASE_LABEL_LEFT_X, design))
    children.append(make_inset_text("0-100% RM", BASE_LABEL_RIGHT_X, design))
    children.append(
        make_inset_text(
            EXPORT_MODE_LABEL,
            BASE_MODE_LABEL_X,
            design,
            BASE_MODE_LABEL_Y,
        )
    )
    children.extend(inset_markers)
    # Inset fills precede the frame so they win on their shared top surfaces.
    children.append(frame)

    return (
        pv.Union(0.0, children),
        sample_records,
        gradient_record,
        marker_records,
        design,
    )


def build_root(desired_x_length):
    if not math.isfinite(desired_x_length) or desired_x_length <= 0.0:
        raise RuntimeError("DESIRED_X_LENGTH must be positive and finite.")

    unscaled_root, sample_records, gradient_record, marker_records, design = (
        build_unscaled_root()
    )
    scale_factor = desired_x_length / BASE_FINISHED_X_LENGTH
    root = pv.Scale(scale_factor, unscaled_root)
    return (
        root,
        sample_records,
        gradient_record,
        marker_records,
        design,
        scale_factor,
    )


def prepared_bounding_box(root):
    bandwidth = max(voxel_size.x, voxel_size.y, voxel_size.z) * 6.0
    root.prepare(voxel_size, bandwidth)
    return root.bounding_box()


def sampled_volume_fractions(root, x, y, z):
    signed_distance, samples = root.sample(x, y, z)
    if signed_distance is None or signed_distance > 0.0 or samples is None:
        raise RuntimeError(
            "Expected an interior material sample at ({:.6f}, {:.6f}, {:.6f}).".format(
                x,
                y,
                z,
            )
        )
    if not samples.has_sample(pv.DefaultAttributes.VOLUME_FRACTIONS):
        raise RuntimeError("Interior sample is missing volume_fractions.")
    return samples.get_sample(pv.DefaultAttributes.VOLUME_FRACTIONS)


def validate_root(
    desired_x_length,
    root,
    sample_records,
    gradient_record,
    marker_records,
    design,
    scale_factor,
    bbox_min,
    bbox_max,
):
    final_x_length = bbox_max.x - bbox_min.x
    if abs(final_x_length - desired_x_length) > DIMENSION_TOLERANCE:
        raise RuntimeError(
            "Expected x length {:.6f} mm, got {:.6f} mm.".format(
                desired_x_length,
                final_x_length,
            )
        )

    expected_y_length = BASE_FINISHED_Y_WIDTH * scale_factor
    final_y_length = bbox_max.y - bbox_min.y
    if abs(final_y_length - expected_y_length) > DIMENSION_TOLERANCE:
        raise RuntimeError(
            "Expected y length {:.6f} mm, got {:.6f} mm.".format(
                expected_y_length,
                final_y_length,
            )
        )

    expected_z_length = (
        BASE_SAMPLE_THICKNESS_Z + BASE_BORDER_EXTENSION_Z
    ) * scale_factor
    final_z_length = bbox_max.z - bbox_min.z
    if abs(final_z_length - expected_z_length) > DIMENSION_TOLERANCE:
        raise RuntimeError(
            "Expected z length {:.6f} mm, got {:.6f} mm.".format(
                expected_z_length,
                final_z_length,
            )
        )

    levels = [record["percent"] for record in sample_records]
    if levels != list(range(0, 101, 5)):
        raise RuntimeError("Sample grid is not ordered from 0% to 100%.")

    gradient_x_length = (
        gradient_record["x_bounds"][1] - gradient_record["x_bounds"][0]
    )
    gradient_y_length = (
        gradient_record["y_bounds"][1] - gradient_record["y_bounds"][0]
    )
    gradient_z_length = (
        gradient_record["z_bounds"][1] - gradient_record["z_bounds"][0]
    )
    if abs(gradient_x_length - BASE_TEST_X_LENGTH) > DIMENSION_TOLERANCE:
        raise RuntimeError("Gradient does not span the complete test width.")
    if abs(gradient_y_length - design["block_y"]) > DIMENSION_TOLERANCE:
        raise RuntimeError("Gradient height does not match a swatch.")
    if abs(gradient_z_length - BASE_SAMPLE_THICKNESS_Z) > DIMENSION_TOLERANCE:
        raise RuntimeError("Gradient thickness does not match a swatch.")

    divider_y_width = design["divider_y_max"] - design["divider_y_min"]
    if abs(divider_y_width - BASE_DIFFUSION_DIVIDER_Y_WIDTH) > (
        DIMENSION_TOLERANCE
    ):
        raise RuntimeError("Diffusion divider width is incorrect.")

    divider_y = (
        design["divider_y_min"] + design["divider_y_max"]
    ) / 2.0 * scale_factor
    for x_fraction in (0.1, 0.5, 0.9):
        divider_x = (
            design["test_x_min"] + BASE_TEST_X_LENGTH * x_fraction
        ) * scale_factor
        signed_distance, _ = root.sample(divider_x, divider_y, 0.0)
        if signed_distance is not None and signed_distance <= 0.0:
            raise RuntimeError("Diffusion divider is not void across the test region.")

    gradient_y = gradient_record["center"][1] * scale_factor
    for expected_fraction in (0.1, 0.5, 0.9):
        sample_x = (
            design["test_x_min"] + BASE_TEST_X_LENGTH * expected_fraction
        ) * scale_factor
        fractions = sampled_volume_fractions(root, sample_x, gradient_y, 0.0)
        radio_fraction = fractions.get(radio_matrix_id, 0.0)
        black_fraction = fractions.get(vero_black_id, 0.0)
        if abs(radio_fraction - expected_fraction) > FRACTION_TOLERANCE:
            raise RuntimeError("Gradient RadioMatrix fraction validation failed.")
        if abs(black_fraction - (1.0 - expected_fraction)) > FRACTION_TOLERANCE:
            raise RuntimeError("Gradient VeroBlack fraction validation failed.")

    if len(marker_records) != 4:
        raise RuntimeError("Expected four orientation marker pairs.")
    for marker_record in marker_records:
        marker_x = marker_record["center"][0] * scale_factor
        marker_y = marker_record["center"][1] * scale_factor
        in_plane_fractions = sampled_volume_fractions(
            root,
            marker_x,
            marker_y,
            0.0,
        )
        if abs(in_plane_fractions.get(radio_matrix_id, 0.0) - 1.0) > (
            FRACTION_TOLERANCE
        ):
            raise RuntimeError("In-plane orientation marker is not RadioMatrix.")

        inset_sample_z = (
            design["top_z"] + BASE_BORDER_EXTENSION_Z / 2.0
        ) * scale_factor
        inset_fractions = sampled_volume_fractions(
            root,
            marker_x,
            marker_y,
            inset_sample_z,
        )
        if abs(inset_fractions.get(label_material_id, 0.0) - 1.0) > (
            FRACTION_TOLERANCE
        ):
            raise RuntimeError("Inset orientation marker is not VeroPureWht.")

        in_plane_z_max = marker_record["in_plane_z_bounds"][1]
        inset_z_min, inset_z_max = marker_record["inset_z_bounds"]
        if abs(in_plane_z_max - design["top_z"]) > DIMENSION_TOLERANCE:
            raise RuntimeError("RadioMatrix marker extends outside the test Z range.")
        if inset_z_min < design["top_z"]:
            raise RuntimeError("Visible marker intrudes into the test Z range.")
        expected_border_top = design["top_z"] + BASE_BORDER_EXTENSION_Z
        if abs(inset_z_max - expected_border_top) > DIMENSION_TOLERANCE:
            raise RuntimeError("Visible marker is not flush with the border top.")

    if pv.DefaultAttributes.VOLUME_FRACTIONS not in root.attribute_list():
        raise RuntimeError("The calibration phantom is missing volume_fractions.")


def build_prepared_root(desired_x_length):
    (
        root,
        sample_records,
        gradient_record,
        marker_records,
        design,
        scale_factor,
    ) = build_root(desired_x_length)
    bbox_min, bbox_max = prepared_bounding_box(root)
    validate_root(
        desired_x_length,
        root,
        sample_records,
        gradient_record,
        marker_records,
        design,
        scale_factor,
        bbox_min,
        bbox_max,
    )
    return (
        root,
        sample_records,
        gradient_record,
        marker_records,
        design,
        scale_factor,
        bbox_min,
        bbox_max,
    )


def format_vec3(vec):
    return "({:.4f}, {:.4f}, {:.4f})".format(vec.x, vec.y, vec.z)


def format_size_value(value):
    rounded = round(value, 1)
    text = "{:.1f}".format(rounded).rstrip("0").rstrip(".")
    return text.replace(".", "p")


def x_size_slug_from_bbox(bbox_min, bbox_max):
    x_length = bbox_max.x - bbox_min.x
    return "x{}mm".format(format_size_value(x_length))


def output_dir_for_root(bbox_min, bbox_max):
    return os.path.join(
        output_root_dir,
        "radiomatrix_veroblack_calibration_{}_{}".format(
            x_size_slug_from_bbox(bbox_min, bbox_max),
            EXPORT_MODE_SLUG,
        ),
    )


def print_material_metadata():
    print("material definitions:")
    print("  {} id: {}".format(RADIO_MATRIX_MATERIAL, radio_matrix_id))
    print("  {} id: {}".format(VERO_BLACK_MATERIAL, vero_black_id))
    print("  {} id: {}".format(LABEL_MATERIAL, label_material_id))


def print_design_metadata(
    desired_x_length,
    scale_factor,
    bbox_min,
    bbox_max,
    design,
    gradient_record,
    marker_records,
):
    x_length = bbox_max.x - bbox_min.x
    y_length = bbox_max.y - bbox_min.y
    z_length = bbox_max.z - bbox_min.z
    print("design: CU scanner HU calibration phantom")
    print("  material assignment mode:", EXPORT_MODE_LABEL.removeprefix("MODE: "))
    print("  desired x length: {:.4f} mm".format(desired_x_length))
    print("  final uniform scale: {:.8f}".format(scale_factor))
    print("  bbox min:", format_vec3(bbox_min))
    print("  bbox max:", format_vec3(bbox_max))
    print(
        "  final size: {:.4f} x {:.4f} x {:.4f} mm".format(
            x_length,
            y_length,
            z_length,
        )
    )
    print("  border width: {:.4f} mm".format(BASE_BORDER_WIDTH * scale_factor))
    print("  sample block x: {:.6f} mm".format(design["block_x"] * scale_factor))
    print("  sample block y: {:.6f} mm".format(design["block_y"] * scale_factor))
    print("  sample thickness z: {:.6f} mm".format(BASE_SAMPLE_THICKNESS_Z * scale_factor))
    divider_width = BASE_DIFFUSION_DIVIDER_Y_WIDTH * scale_factor
    print(
        "  void diffusion divider: {:.4f} mm ({:.2f} y voxels)".format(
            divider_width,
            divider_width / voxel_size.y,
        )
    )
    print(
        "  gradient: left-to-right 0-100% RM, x [{:.4f}, {:.4f}] mm".format(
            gradient_record["x_bounds"][0] * scale_factor,
            gradient_record["x_bounds"][1] * scale_factor,
        )
    )
    print("  orientation markers:")
    for marker_record in marker_records:
        print(
            "    {}: {} at ({:.4f}, {:.4f}) mm".format(
                marker_record["corner"],
                marker_record["shape"],
                marker_record["center"][0] * scale_factor,
                marker_record["center"][1] * scale_factor,
            )
        )


def print_sample_ratio_map(sample_records, scale_factor):
    print("sample ratio map:")
    print("idx row col  RM%  center_xyz                 x_bounds             y_bounds")
    for record in sample_records:
        cx, cy, cz = record["center"]
        x_min, x_max = record["x_bounds"]
        y_min, y_max = record["y_bounds"]
        print(
            "{idx:>3} {row:>3} {col:>3} {pct:>4}  "
            "({cx:>8.4f}, {cy:>7.4f}, {cz:>6.3f})  "
            "[{x0:>8.4f}, {x1:>8.4f}]  "
            "[{y0:>7.4f}, {y1:>7.4f}]".format(
                idx=record["index"],
                row=record["row"],
                col=record["col"],
                pct=record["percent"],
                cx=cx * scale_factor,
                cy=cy * scale_factor,
                cz=cz * scale_factor,
                x0=x_min * scale_factor,
                x1=x_max * scale_factor,
                y0=y_min * scale_factor,
                y1=y_max * scale_factor,
            )
        )


def on_progress(progress):
    print("compile progress: {:.1f}%".format(100.0 * progress))


def compile_root(root, bbox_min, bbox_max):
    output_dir = output_dir_for_root(bbox_min, bbox_max)

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


print_material_metadata()

(
    root,
    sample_records,
    gradient_record,
    marker_records,
    design,
    scale_factor,
    bbox_min,
    bbox_max,
) = build_prepared_root(DESIRED_X_LENGTH)

print()
print_design_metadata(
    DESIRED_X_LENGTH,
    scale_factor,
    bbox_min,
    bbox_max,
    design,
    gradient_record,
    marker_records,
)
print_sample_ratio_map(sample_records, scale_factor)

if ENABLE_RENDER:
    viz.Render(root, materials)

if RUN_MATERIAL_INKJET_COMPILER:
    compile_root(root, bbox_min, bbox_max)
