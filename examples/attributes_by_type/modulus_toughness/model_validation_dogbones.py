import os

import pyvcad as pv
import pyvcad_attribute_resolver as resolver
import pyvcad_compilers as pvc

ENABLE_RENDER = True
ENABLE_COMPILE = True

# Pick the actual materials we will use for the soft, rigid, and liquid roles
# in the modulus/toughness mapping.
materials = pv.j750_materials
SOFT_MATERIAL = "Agilus30Clr"
RIGID_MATERIAL = "VeroBlack"
RIGID_MATERIAL_CONTRAST = "VeroPureWht"
LIQUID_MATERIAL = "M.Cleanser"
rigid_material_id = materials.id(RIGID_MATERIAL)
rigid_material_contrast_id = materials.id(RIGID_MATERIAL_CONTRAST)
rigid_tab_volume_fractions = pv.VolumeFractionsAttribute([(1.0, rigid_material_id)])
rigid_contrast_volume_fractions = pv.VolumeFractionsAttribute(
    [(1.0, rigid_material_contrast_id)]
)

# How many copies of each modulus/toughness pair to make, with different
# repeat labels.
repeat_count = 1

# The first repeat label to use. For example, "A" with repeat_count = 3 creates
# labels A, B, C, while "D" creates D, E, F.
repeat_start_letter = "A"

# The J750 has a 490x390 mm bed, but we need to leave some margin, so we
# configure a slightly smaller effective bed size.
printer_bed_size_x = 480.0
printer_bed_size_y = 380.0

# The spacing between dogbones when laid out on the bed. This should be large
# enough to prevent them from fusing together during printing.
sample_spacing = 3.0

# The center test plateau length and pure rigid tab plateau length are both
# measured along X on the centered dogbone.
test_region_width = 45.0
tab_width = 17.0

# Pairs of (desired modulus in MPa, desired toughness in MJ/m^3) for the
# test region of each dogbone.
dogbone_targets = [
    (0.197370061867259, 0.31093620219635737),
    (1.3616482290327747, 3.7347788829246786),
    (313.96249010189223, 0.8404648867439365),
    (330.62457455352205, 5.782157820180565),
    (789.9236445798632, 4.025202375374276),
    (0.46822539069408137, 0.7299401657003852),
    (1.8139030082476428, 2.288881473111886),
    (2.438188772194951, 2.8412885657150224),
    (22.071657478841914, 1.170907727252675),
    (45.991597267269945, 3.6524456371266214),
    (185.5364838386748, 5.183281374842095),
    (670.9113718923139, 5.9567081292637125),
    (2.2122813630313973, 0.8790406294143741),
    (11.620279174590134, 0.8790406294143744),
    (60.960798288501394, 0.8790406294143724),
]

# Compile (export settings)
voxel_size = pv.Vec3(0.0423, 0.0846, 0.027)  # J750's asymmetric voxel size in mm
liquid_keep_out_distance = 0.0  # How close liquid can be to the surface of the part.
output_dir = os.path.join(
    os.path.dirname(__file__),
    "dogbone_output",
)
prefix = "slice_"

dogbone_base = pv.Mesh("tensile_ASTM_D412-C.stl", center=True, override_voxel_size=0.25)
bbox_min, bbox_max = dogbone_base.bounding_box()
object_length = bbox_max.x - bbox_min.x
object_width = bbox_max.y - bbox_min.y
object_height = bbox_max.z - bbox_min.z
half_object_length = object_length / 2.0
half_object_width = object_width / 2.0
top_surface_z = bbox_max.z

if test_region_width <= 0.0:
    raise ValueError("test_region_width must be positive.")
if tab_width <= 0.0:
    raise ValueError("tab_width must be positive.")

half_test = test_region_width / 2.0
x_tab_inner = half_object_length - tab_width
blend_width = x_tab_inner - half_test
if blend_width <= 0.0:
    raise ValueError(
        "test_region_width and tab_width leave no room for a blend region."
    )

left_tab_max_x = -half_test - blend_width
left_blend_min_x = left_tab_max_x
left_blend_max_x = -half_test
right_blend_min_x = half_test
right_blend_max_x = half_test + blend_width
right_tab_min_x = right_blend_max_x

text_depth_fraction = 0.35
text_depth = object_height * text_depth_fraction
text_font = "Arial"
text_font_aspect = pv.FontAspect.Regular
text_h_align = pv.HorizontalAlignment.Center
text_v_align = pv.VerticalAlignment.Center
text_center_z = top_surface_z - text_depth / 2.0

property_label_center_x = half_object_length - tab_width / 2.0
property_label_center_offset_y = object_width * 0.3
property_label_margin_x = 1.0
property_label_margin_y = 1.0
property_label_available_width = tab_width - 2.0 * property_label_margin_x
property_label_available_height = 2.0 * (
    half_object_width - property_label_center_offset_y - property_label_margin_y
)

if property_label_available_width <= 0.0 or property_label_available_height <= 0.0:
    raise ValueError("Tab text placement leaves no room for the inset labels.")

repeat_label_center_x = -property_label_center_x
repeat_label_margin_x = 1.5
repeat_label_margin_y = 2.0
repeat_label_available_width = tab_width - 2.0 * repeat_label_margin_x
repeat_label_available_height = object_width - 2.0 * repeat_label_margin_y

if repeat_label_available_width <= 0.0 or repeat_label_available_height <= 0.0:
    raise ValueError("Tab text placement leaves no room for the repeat label.")


def measure_text_size(text_string, text_height):
    text_probe = pv.Text(
        text_string,
        text_height,
        text_depth,
        text_font_aspect,
        text_font,
        text_h_align,
        text_v_align,
    )
    probe_bbox_min, probe_bbox_max = text_probe.bounding_box()
    return (
        probe_bbox_max.x - probe_bbox_min.x,
        probe_bbox_max.y - probe_bbox_min.y,
    )


def compute_fitting_text_height(reference_strings, available_width, available_height):
    reference_text_height = 10.0
    max_reference_width = 0.0
    max_reference_height = 0.0

    for text_string in reference_strings:
        reference_width, reference_height = measure_text_size(
            text_string,
            reference_text_height,
        )
        if reference_width > max_reference_width:
            max_reference_width = reference_width
        if reference_height > max_reference_height:
            max_reference_height = reference_height

    return reference_text_height * min(
        available_width / max_reference_width,
        available_height / max_reference_height,
    )


property_text_height = compute_fitting_text_height(
    ["M\n3507.000", "T\n99.999"],
    property_label_available_width,
    property_label_available_height,
)
repeat_text_height = compute_fitting_text_height(
    ["W"],
    repeat_label_available_width,
    repeat_label_available_height,
)
repeat_text_scale = 0.5
repeat_text_height *= repeat_text_scale

center_fraction_cache = {}


def normalize_repeat_start_letter(start_letter):
    if not isinstance(start_letter, str):
        raise ValueError("repeat_start_letter must be a single letter from A to Z.")

    normalized_letter = start_letter.strip().upper()
    if len(normalized_letter) != 1 or not "A" <= normalized_letter <= "Z":
        raise ValueError("repeat_start_letter must be a single letter from A to Z.")

    return normalized_letter


def repeat_label_for_index(repeat_index, start_letter):
    normalized_letter = normalize_repeat_start_letter(start_letter)
    start_index = ord(normalized_letter) - ord("A")
    repeat_letter_index = start_index + repeat_index
    if repeat_index < 0 or repeat_letter_index >= 26:
        raise ValueError(
            "repeat_count and repeat_start_letter must produce labels from A to Z."
        )
    return chr(ord("A") + repeat_letter_index)


def expand_dogbone_requests(targets, repeat_count, repeat_start_letter):
    if repeat_count < 1:
        raise ValueError("repeat_count must be at least 1.")
    normalized_start_letter = normalize_repeat_start_letter(repeat_start_letter)
    start_index = ord(normalized_start_letter) - ord("A")
    if start_index + repeat_count > 26:
        raise ValueError(
            "repeat_count and repeat_start_letter must produce labels from A to Z."
        )
    if not targets:
        raise ValueError("dogbone_targets must contain at least one modulus/toughness pair.")

    requests = []
    for desired_modulus_mpa, desired_toughness_min_mj_per_m3 in targets:
        for repeat_index in range(repeat_count):
            requests.append(
                (
                    desired_modulus_mpa,
                    desired_toughness_min_mj_per_m3,
                    repeat_label_for_index(repeat_index, normalized_start_letter),
                )
            )
    return requests


def make_region_prism(x_min, x_max):
    return pv.RectPrism.FromMinAndMax(
        pv.Vec3(x_min, bbox_min.y, bbox_min.z),
        pv.Vec3(x_max, bbox_max.y, bbox_max.z),
    )


def blend_parameter_expr(x_start, x_end, reverse=False):
    span = x_end - x_start
    if reverse:
        numerator = f"({x_end:.8f} - x)"
    else:
        numerator = f"(x - {x_start:.8f})"
    return f"max(min({numerator} / {span:.8f}, 1.0), 0.0)"


def resolve_center_endpoint_fractions(
    center_region,
    desired_modulus_mpa,
    desired_toughness_min_mj_per_m3,
):
    cache_key = (desired_modulus_mpa, desired_toughness_min_mj_per_m3)
    if cache_key in center_fraction_cache:
        return center_fraction_cache[cache_key]

    center_region_clone = center_region.clone()
    center_region_clone.prepare(pv.Vec3(1,1,1), 1.0) # Coarse preparation since we just want a rough estimate of the fractions at the center
    signed_distance, samples = center_region_clone.sample(0.0, 0.0, 0.0)
    if signed_distance is None or samples is None:
        raise RuntimeError("Failed to sample the resolved center region.")
    if not samples.has_sample(pv.DefaultAttributes.VOLUME_FRACTIONS):
        raise RuntimeError("The resolved center region is missing volume_fractions.")

    sampled_fractions = samples.get_sample(pv.DefaultAttributes.VOLUME_FRACTIONS)
    fractions = (
        float(sampled_fractions.get(materials.id(SOFT_MATERIAL), 0.0)),
        float(sampled_fractions.get(rigid_material_id, 0.0)),
        float(sampled_fractions.get(materials.id(LIQUID_MATERIAL), 0.0)),
    )
    center_fraction_cache[cache_key] = fractions
    return fractions


def make_blend_volume_fractions(u_expr, center_soft, center_rigid, center_liquid):
    return pv.VolumeFractionsAttribute(
        [
            (f"({center_soft:.12f}) * ({u_expr})", materials.id(SOFT_MATERIAL)),
            (
                f"1.0 + ({center_rigid - 1.0:.12f}) * ({u_expr})",
                rigid_material_id,
            ),
            (f"({center_liquid:.12f}) * ({u_expr})", materials.id(LIQUID_MATERIAL)),
        ]
    )


def make_dogbone(
    x_offset,
    y_offset,
    desired_modulus_mpa,
    desired_toughness_min_mj_per_m3,
    repeat_label,
):
    dogbone = dogbone_base.clone()

    label_text_modulus = f"M\n{desired_modulus_mpa:.3f}"
    label_text_toughness = f"T\n{desired_toughness_min_mj_per_m3:.3f}"

    modulus_text = pv.Text(
        label_text_modulus,
        property_text_height,
        text_depth,
        text_font_aspect,
        text_font,
        text_h_align,
        text_v_align,
    )
    modulus_text = pv.Translate(
        property_label_center_x,
        property_label_center_offset_y,
        text_center_z,
        modulus_text,
    )

    toughness_text = pv.Text(
        label_text_toughness,
        property_text_height,
        text_depth,
        text_font_aspect,
        text_font,
        text_h_align,
        text_v_align,
    )
    toughness_text = pv.Translate(
        property_label_center_x,
        -property_label_center_offset_y,
        text_center_z,
        toughness_text,
    )

    repeat_text = pv.Text(
        repeat_label,
        repeat_text_height,
        text_depth,
        text_font_aspect,
        text_font,
        text_h_align,
        text_v_align,
    )
    repeat_text = pv.Translate(
        repeat_label_center_x,
        0.0,
        text_center_z,
        repeat_text,
    )

    property_text_union = pv.BBoxUnion([modulus_text, toughness_text])
    right_tab_inlay_region = pv.Intersection(
        property_text_union,
        make_region_prism(right_tab_min_x, half_object_length),
    )
    left_tab_inlay_region = pv.Intersection(
        repeat_text,
        make_region_prism(-half_object_length, left_tab_max_x),
    )

    center_region = pv.Intersection(
        dogbone,
        make_region_prism(-half_test, half_test),
    )
    left_blend_region = pv.Intersection(
        dogbone,
        make_region_prism(left_blend_min_x, left_blend_max_x),
    )
    right_blend_region = pv.Intersection(
        dogbone,
        make_region_prism(right_blend_min_x, right_blend_max_x),
    )
    left_tab_region = pv.Intersection(
        dogbone,
        make_region_prism(-half_object_length, left_tab_max_x),
    )
    left_tab_region = pv.Difference(left_tab_region, left_tab_inlay_region)
    right_tab_region = pv.Intersection(
        dogbone,
        make_region_prism(right_tab_min_x, half_object_length),
    )
    right_tab_region = pv.Difference(right_tab_region, right_tab_inlay_region)

    center_region.set_attribute(
        pv.DefaultAttributes.MODULUS,
        pv.FloatAttribute(desired_modulus_mpa),
    )
    center_region.set_attribute(
        pv.DefaultAttributes.TOUGHNESS,
        pv.FloatAttribute(desired_toughness_min_mj_per_m3),
    )
    center_region = resolver.adapt(
        center_region,
        [pv.DefaultAttributes.VOLUME_FRACTIONS],
        tags=["j750_modulus_toughness"],
    )

    center_soft, center_rigid, center_liquid = resolve_center_endpoint_fractions(
        center_region,
        desired_modulus_mpa,
        desired_toughness_min_mj_per_m3,
    )

    left_blend_region.set_attribute(
        pv.DefaultAttributes.VOLUME_FRACTIONS,
        make_blend_volume_fractions(
            blend_parameter_expr(left_blend_min_x, left_blend_max_x),
            center_soft,
            center_rigid,
            center_liquid,
        ),
    )
    right_blend_region.set_attribute(
        pv.DefaultAttributes.VOLUME_FRACTIONS,
        make_blend_volume_fractions(
            blend_parameter_expr(right_blend_min_x, right_blend_max_x, reverse=True),
            center_soft,
            center_rigid,
            center_liquid,
        ),
    )
    left_tab_region.set_attribute(
        pv.DefaultAttributes.VOLUME_FRACTIONS,
        rigid_tab_volume_fractions,
    )
    right_tab_region.set_attribute(
        pv.DefaultAttributes.VOLUME_FRACTIONS,
        rigid_tab_volume_fractions,
    )
    left_tab_inlay_region.set_attribute(
        pv.DefaultAttributes.VOLUME_FRACTIONS,
        rigid_contrast_volume_fractions,
    )
    right_tab_inlay_region.set_attribute(
        pv.DefaultAttributes.VOLUME_FRACTIONS,
        rigid_contrast_volume_fractions,
    )

    hybrid = pv.Union()
    hybrid.add_child(left_tab_region)
    hybrid.add_child(left_tab_inlay_region)
    hybrid.add_child(left_blend_region)
    hybrid.add_child(center_region)
    hybrid.add_child(right_blend_region)
    hybrid.add_child(right_tab_region)
    hybrid.add_child(right_tab_inlay_region)

    translate = pv.Translate(x_offset, y_offset, 0.0, hybrid)
    return translate


def build_dogbone_grid(
    targets,
    repeat_count,
    repeat_start_letter,
    bed_size_x,
    bed_size_y,
):
    if bed_size_x <= 0.0 or bed_size_y <= 0.0:
        raise ValueError("printer_bed_size_x and printer_bed_size_y must be positive.")

    requests = expand_dogbone_requests(targets, repeat_count, repeat_start_letter)
    pitch_x = object_length + sample_spacing
    pitch_y = object_width + sample_spacing
    max_columns = int((bed_size_x + sample_spacing) // pitch_x)
    max_rows = int((bed_size_y + sample_spacing) // pitch_y)
    capacity = max_columns * max_rows

    if capacity <= 0:
        raise ValueError(
            "The printer bed is too small for one dogbone. "
            f"Dogbone footprint with spacing is {pitch_x:.3f} x {pitch_y:.3f} mm, "
            f"bed size is {bed_size_x:.3f} x {bed_size_y:.3f} mm."
        )

    if len(requests) > capacity:
        raise ValueError(
            f"Requested {len(requests)} dogbones but the configured build plate fits "
            f"at most {capacity}."
        )

    bbox_union = pv.BBoxUnion()
    for specimen_index, request in enumerate(requests):
        desired_modulus_mpa, desired_toughness_min_mj_per_m3, repeat_label = request
        i = specimen_index % max_columns
        j = specimen_index // max_columns
        x_offset = half_object_length + i * pitch_x
        y_offset = half_object_width + j * pitch_y
        bbox_union.add_child(
            make_dogbone(
                x_offset,
                y_offset,
                desired_modulus_mpa,
                desired_toughness_min_mj_per_m3,
                repeat_label,
            )
        )

    return bbox_union


resolver.clear_conversions()
resolver.register_j750_modulus_toughness_conversions(
    material_defs=materials,
    rigid_material=RIGID_MATERIAL,
    soft_material=SOFT_MATERIAL,
    liquid_material=LIQUID_MATERIAL,
)

root = build_dogbone_grid(
    dogbone_targets,
    repeat_count,
    repeat_start_letter,
    printer_bed_size_x,
    printer_bed_size_y,
)

attribute_names = root.attribute_list()
if pv.DefaultAttributes.VOLUME_FRACTIONS not in attribute_names:
    raise RuntimeError("The resolved tree is missing the volume_fractions attribute.")

if ENABLE_RENDER:
    import pyvcad_rendering as viz
    viz.Render(root, materials)


def on_progress(progress):
    print("compile progress: {:.1f}%".format(100.0 * progress))


if ENABLE_COMPILE:
    compiler = pvc.MaterialInkjetCompiler(
        root,
        voxel_size,
        output_dir,
        prefix,
        materials,
        0.0,
    )
    compiler.set_progress_callback(on_progress)
    compiler.compile()
    print("output directory:", output_dir)
    print("resolution (x, y, z png count):", compiler.resolution())
    print("material voxel counts:", compiler.material_voxel_counts())
