"""
Color Inkjet - stochastic vs 3D dithered comparison
===================================================

Builds a compact full-color palette plaque and exports it with both
ColorInkjetCompiler modes across selected color-pipeline step combinations.
"""
from pathlib import Path
import shutil

import pyvcad as pv
import pyvcad_compilers as pvc
import pyvcad_rendering as viz


EXPORT = True
RENDER_PREVIEW = True
PREVIEW_EXPORT_MODE = pvc.ColorInkjetExportMode.DITHERED_3D
PREVIEW_PIPELINE_CASE = "full_pipeline"

voxel_size = pv.Vec3(0.0423, 0.0846, 0.027)
prefix = "slice_"

script_dir = Path(__file__).resolve().parent
output_root = script_dir / "output"
icc_profiles_dir = Path(pvc.__file__).resolve().parent / "icc_profiles"
if not icc_profiles_dir.is_dir():
    icc_profiles_dir = script_dir.parents[2] / "compilers" / "icc_profiles"
pvc.ColorPipeline.set_icc_resource_path(str(icc_profiles_dir))


plaque_width = 80.0
face_scale = plaque_width / 28.0
plaque_height = 19.25 * face_scale
base_thickness = 0.81
feature_thickness = 0.405
text_depth = 0.405

margin = 1.0 * face_scale
gap = 0.30 * face_scale
swatch_size = 2.95 * face_scale
swatch_columns = 8
palette_width = swatch_columns * swatch_size + (swatch_columns - 1) * gap

gradient_height = 1.8 * face_scale
gradient_count = 3
gradient_total_height = gradient_count * gradient_height + (gradient_count - 1) * gap
label_height = 3.2 * face_scale
section_gap = 0.65 * face_scale
mode_text_height = 0.95 * face_scale
case_text_height = 0.72 * face_scale
flags_text_height = 0.42 * face_scale
label_line_offset = 0.95 * face_scale

base_top = base_thickness / 2.0
feature_z = base_top + feature_thickness / 2.0
text_z = base_top + feature_thickness + text_depth / 2.0

content_top = plaque_height / 2.0 - margin
label_y = content_top - label_height / 2.0
gradient_top = label_y - label_height / 2.0 - section_gap
swatch_top = gradient_top - gradient_total_height - section_gap


def color_attribute(r, g, b, a=1.0):
    return pv.Vec4Attribute(r, g, b, a)


def pipeline_options(first_gamma, icc_profile, second_gamma, affinity_blend):
    options = pvc.ColorPipelineOptions()
    options.first_gamma_enabled = first_gamma
    options.icc_profile_enabled = icc_profile
    options.second_gamma_enabled = second_gamma
    options.affinity_blend_enabled = affinity_blend
    return options


def step_flags(options):
    def on_off(enabled):
        return "ON" if enabled else "OFF"

    return "G1 {}  ICC {}  G2 {}  AFF {}".format(
        on_off(options.first_gamma_enabled),
        on_off(options.icc_profile_enabled),
        on_off(options.second_gamma_enabled),
        on_off(options.affinity_blend_enabled),
    )


def add_box(children, center_x, center_y, size_x, size_y, size_z, attr, center_z):
    box = pv.RectPrism(
        pv.Vec3(center_x, center_y, center_z),
        pv.Vec3(size_x, size_y, size_z),
    )
    box.set_attribute(pv.DefaultAttributes.COLOR_RGBA, attr)
    children.append(box)
    return box


solid_colors = [
    ("red", (1.0, 0.0, 0.0)),
    ("green", (0.0, 1.0, 0.0)),
    ("blue", (0.0, 0.0, 1.0)),
    ("cyan", (0.0, 1.0, 1.0)),
    ("magenta", (1.0, 0.0, 1.0)),
    ("yellow", (1.0, 1.0, 0.0)),
    ("white", (1.0, 1.0, 1.0)),
    ("black", (0.0, 0.0, 0.0)),
    ("gray25", (0.25, 0.25, 0.25)),
    ("gray50", (0.50, 0.50, 0.50)),
    ("gray75", (0.75, 0.75, 0.75)),
    ("orange", (1.0, 0.50, 0.0)),
    ("purple", (0.50, 0.0, 0.70)),
    ("brown", (0.45, 0.25, 0.10)),
    ("pink", (1.0, 0.41, 0.70)),
]


pipeline_cases = [
    (
        "no_pipeline",
        "NO PIPELINE STEPS",
        pipeline_options(False, False, False, False),
    ),
    (
        "icc_only",
        "ICC ONLY",
        pipeline_options(False, True, False, False),
    ),
    (
        "first_gamma_only",
        "FIRST GAMMA ONLY",
        pipeline_options(True, False, False, False),
    ),
    (
        "first_gamma_icc",
        "FIRST GAMMA + ICC",
        pipeline_options(True, True, False, False),
    ),
    (
        "icc_gamma",
        "ICC + GAMMA",
        pipeline_options(False, True, True, False),
    ),
    (
        "full_pipeline",
        "FULL PIPELINE",
        pipeline_options(True, True, True, True),
    ),
]

export_modes = [
    ("dithered_3d", "DITHERED 3D", pvc.ColorInkjetExportMode.DITHERED_3D),
    ("stochastic", "STOCHASTIC", pvc.ColorInkjetExportMode.STOCHASTIC),
]


def build_plaque(mode_label, case_label, flags_label):
    children = []

    # Children are ordered front-to-back for overlapping COLOR_RGBA regions. The
    # default conflict resolver keeps the first attribute it sees.
    for text, height, y_offset in [
        (mode_label, mode_text_height, label_line_offset),
        (case_label, case_text_height, 0.0),
        (flags_label, flags_text_height, -label_line_offset),
    ]:
        label_text = pv.Text(
            text,
            height,
            text_depth,
            pv.FontAspect.Bold,
            "Consolas",
            pv.HorizontalAlignment.Center,
            pv.VerticalAlignment.Center,
        )
        label_text.set_attribute(
            pv.DefaultAttributes.COLOR_RGBA,
            color_attribute(0.0, 0.0, 0.0, 1.0),
        )
        children.append(pv.Translate(0.0, label_y + y_offset, text_z, label_text))

    swatch_start_x = -palette_width / 2.0 + swatch_size / 2.0
    swatch_start_y = swatch_top - swatch_size / 2.0

    for index, (_, rgb) in enumerate(solid_colors):
        column = index % swatch_columns
        row = index // swatch_columns
        x = swatch_start_x + column * (swatch_size + gap)
        y = swatch_start_y - row * (swatch_size + gap)
        add_box(
            children,
            x,
            y,
            swatch_size,
            swatch_size,
            feature_thickness,
            color_attribute(rgb[0], rgb[1], rgb[2], 1.0),
            feature_z,
        )

    gradient_left = -palette_width / 2.0
    gradient_width = palette_width
    gradient_start_y = gradient_top - gradient_height / 2.0
    t_expr = "(x - ({:.6f})) / {:.6f}".format(gradient_left, gradient_width)

    gradients = [
        ("red to green", "1.0 - ({})".format(t_expr), t_expr, "0.05"),
        ("blue to yellow", t_expr, t_expr, "1.0 - ({})".format(t_expr)),
        ("black to white", t_expr, t_expr, t_expr),
    ]

    for index, (_, r_expr, g_expr, b_expr) in enumerate(gradients):
        y = gradient_start_y - index * (gradient_height + gap)
        add_box(
            children,
            0.0,
            y,
            gradient_width,
            gradient_height,
            feature_thickness,
            color_attribute(r_expr, g_expr, b_expr, "1.0"),
            feature_z,
        )

    add_box(
        children,
        0.0,
        label_y,
        palette_width,
        label_height,
        feature_thickness,
        color_attribute(1.0, 1.0, 1.0, 1.0),
        feature_z,
    )

    add_box(
        children,
        0.0,
        0.0,
        plaque_width,
        plaque_height,
        base_thickness,
        color_attribute(1.0, 1.0, 1.0, 1.0),
        0.0,
    )

    return pv.BBoxUnion(children)


preview_root = None
for mode_slug, mode_label, export_mode in export_modes:
    for case_slug, case_label, options in pipeline_cases:
        if export_mode == PREVIEW_EXPORT_MODE and case_slug == PREVIEW_PIPELINE_CASE:
            preview_root = build_plaque(mode_label, case_label, step_flags(options))

if RENDER_PREVIEW and preview_root is not None:
    viz.Render(preview_root)

if EXPORT:
    for mode_slug, mode_label, export_mode in export_modes:
        for case_slug, case_label, options in pipeline_cases:
            output_name = "{}_{}".format(mode_slug, case_slug)
            output_dir = output_root / output_name
            root = build_plaque(mode_label, case_label, step_flags(options))

            if output_dir.is_dir():
                shutil.rmtree(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)

            compiler = pvc.ColorInkjetCompiler(
                root,
                voxel_size,
                str(output_dir),
                prefix,
                "default",
                export_mode,
                options,
            )

            def on_progress(progress, name=output_name):
                print("{} compile progress: {:.1f}%".format(name, 100.0 * progress))

            compiler.set_progress_callback(on_progress)
            compiler.compile()
            print("{} resolution (x, y, z png count): {}".format(output_name, compiler.resolution()))
            print("wrote PNG stack to:", output_dir)
