"""
Mechanical Properties to J750 Volume Fractions
==============================================

This example models a simple bar directly with modulus and toughness design
intent, then explicitly converts those attributes into J750 volume fractions
using the bundled `j750_modulus_toughness` lookup table.
"""
import os
import shutil

import pyvcad as pv
import pyvcad_attribute_resolver as resolver
import pyvcad_compilers as pvc
from pyvcad_attribute_resolver.modules.j750_modulus_toughness import load_lookup_table

ENABLE_RENDER = True
ENABLE_COMPILE = True

materials = pv.j750_materials

SOFT_MATERIAL = "Agilus30Clr"
RIGID_MATERIAL = "VeroBlack"
LIQUID_MATERIAL = "M.Cleanser"

bar_length = 100.0
bar_width = 25.0
bar_height = 5

modulus_min_mpa = 10.0
modulus_max_mpa = 100.0
toughness_min_mj_per_m3 = 2.0
toughness_max_mj_per_m3 = 4.0

voxel_size = pv.Vec3(0.0423, 0.0846, 0.027)
liquid_keep_out_distance = 0.25
output_dir = os.path.join(
    os.path.dirname(__file__),
    "mechanical_properties_j750_output",
)
prefix = "slice_"


def linear_gradient_expr(value_min, value_max, length):
    value_span = value_max - value_min
    return (
        f"max(min(({value_span:.8f} * (x + {length / 2.0:.8f}) / {length:.8f}) + "
        f"{value_min:.8f}, {value_max:.8f}), {value_min:.8f})"
    )


def build_lookup_table_converter(lookup_table, material_defs):
    soft_id = material_defs.id(SOFT_MATERIAL)
    rigid_id = material_defs.id(RIGID_MATERIAL)
    liquid_id = material_defs.id(LIQUID_MATERIAL)

    modulus_axis_mpa = lookup_table["modulus_axis_mpa"]
    toughness_axis_mj_per_m3 = lookup_table["toughness_axis_mj_per_m3"]
    fraction_grid = lookup_table["fractions"]
    valid_grid = lookup_table["valid"]

    entries = []
    for toughness_index, toughness_mj_per_m3 in enumerate(toughness_axis_mj_per_m3):
        for modulus_index, modulus_mpa in enumerate(modulus_axis_mpa):
            fractions = fraction_grid[toughness_index, modulus_index]
            entry = pv.LookupTableEntry(
                [float(modulus_mpa), float(toughness_mj_per_m3)],
                {
                    soft_id: float(fractions[0]),
                    rigid_id: float(fractions[1]),
                    liquid_id: float(fractions[2]),
                },
            )
            entry.is_valid = bool(valid_grid[toughness_index, modulus_index])
            entries.append(entry)

    return pv.LookupTableConverter(
        [pv.DefaultAttributes.MODULUS, pv.DefaultAttributes.TOUGHNESS],
        [pv.DefaultAttributes.VOLUME_FRACTIONS],
        entries,
        pv.InterpolationMode.LINEAR,
    )


def on_progress(progress):
    print("compile progress: {:.1f}%".format(100.0 * progress))


lookup_table = load_lookup_table()

modulus_expr = linear_gradient_expr(modulus_min_mpa, modulus_max_mpa, bar_length)
toughness_expr = linear_gradient_expr(
    toughness_min_mj_per_m3,
    toughness_max_mj_per_m3,
    bar_length,
)

bar = pv.RectPrism(
    pv.Vec3(0.0, 0.0, 0.0),
    pv.Vec3(bar_length, bar_width, bar_height),
)
bar.set_attribute(
    pv.DefaultAttributes.MODULUS,
    pv.FloatAttribute(modulus_expr),
)
bar.set_attribute(
    pv.DefaultAttributes.TOUGHNESS,
    pv.FloatAttribute(toughness_expr),
)

converter = build_lookup_table_converter(lookup_table, materials)
root = pv.AttributeModifier(converter, bar)

# Optional resolver-based path using the same bundled J750 lookup table:
# resolver.clear_conversions()
# resolver.register_j750_modulus_toughness_conversions(material_defs=materials)
# root = resolver.adapt(bar, ["volume_fractions"], tags=["j750_modulus_toughness"])

attribute_names = root.attribute_list()
if pv.DefaultAttributes.VOLUME_FRACTIONS not in attribute_names:
    raise RuntimeError("The resolved tree is missing the volume_fractions attribute.")

if ENABLE_RENDER:
    import pyvcad_rendering as viz

    viz.Render(root, materials)

if ENABLE_COMPILE:
    if os.path.isdir(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    compiler = pvc.MaterialInkjetCompiler(
        root,
        voxel_size,
        output_dir,
        prefix,
        materials,
        liquid_keep_out_distance,
    )
    compiler.set_progress_callback(on_progress)
    compiler.compile()
    print("output directory:", output_dir)
    print("resolution (x, y, z png count):", compiler.resolution())
    print("material voxel counts:", compiler.material_voxel_counts())
