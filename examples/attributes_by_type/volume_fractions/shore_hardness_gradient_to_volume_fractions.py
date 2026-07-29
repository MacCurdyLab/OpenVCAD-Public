"""
Shore Hardness Gradient to Volume Fractions
===========================================

This example starts with a simple shore-hardness design intent and lets the
attribute resolver synthesize the J750 volume-fraction mixes needed by the
material inkjet compiler.
"""
import os
import shutil

import pyvcad as pv
import pyvcad_attribute_resolver as resolver
import pyvcad_compilers as pvc
import pyvcad_rendering as viz

materials = pv.j750_materials

bar_length = 80.0
bar_width = 16.0
bar_height = 10.0
shore_min = 30.0
shore_max = 100.0

# The bar is centered at the origin, so map x from [-L/2, L/2] into a
# 30A -> 100A design-intent gradient. The resolver clamps values above the
# measured calibration range to the hardest supported J750 mix.
shore_span = shore_max - shore_min
shore_expr = (
    f"max(min(({shore_span:.8f} * (x + {bar_length / 2.0:.8f}) / {bar_length:.8f}) + "
    f"{shore_min:.8f}, {shore_max:.8f}), {shore_min:.8f})"
)

bar = pv.RectPrism(
    pv.Vec3(0.0, 0.0, 0.0),
    pv.Vec3(bar_length, bar_width, bar_height),
)
bar.set_attribute(
    pv.DefaultAttributes.SHORE_HARDNESS,
    pv.FloatAttribute(shore_expr),
)

resolver.clear_conversions()
resolver.register_j750_shore_hardness_conversions(
    material_defs=materials,
    agilus_material="Agilus30Mgn",
    vero_material="VeroYellow",
)

root = resolver.adapt(bar, ["volume_fractions"], tags=["j750_shore_hardness"])

viz.Render(root, materials)

voxel_size = pv.Vec3(0.15, 0.15, 0.15)
output_dir = os.path.join(
    os.path.dirname(__file__),
    "shore_hardness_gradient_slices",
)
prefix = "slice_"

if os.path.isdir(output_dir):
    shutil.rmtree(output_dir)
os.makedirs(output_dir, exist_ok=True)

compiler = pvc.MaterialInkjetCompiler(
    root,
    voxel_size,
    output_dir,
    prefix,
    materials,
    0.0,
)


def on_progress(progress):
    print("compile progress: {:.1f}%".format(100.0 * progress))


compiler.set_progress_callback(on_progress)
compiler.compile()
print("resolution (x, y, z png count):", compiler.resolution())
print("material voxel counts:", compiler.material_voxel_counts())
