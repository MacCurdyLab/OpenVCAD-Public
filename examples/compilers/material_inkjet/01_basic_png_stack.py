"""
Material Inkjet — basic PNG stack
=================================

Builds a small prism with a horizontal volume-fraction gradient (blue ↔ red),
compiles a material-inkjet PNG slice stack, then opens the interactive renderer.

Companion to: docs/source/guides/compilers/material-inkjet.md
"""
import os
import shutil

import pyvcad as pv
import pyvcad_compilers as pvc
import pyvcad_rendering as viz

materials = pv.default_materials

cube = pv.RectPrism(pv.Vec3(0, 0, 0), pv.Vec3(20, 10, 10))
fraction_gradient = pv.VolumeFractionsAttribute(
    [
        ("x/20 + 0.5", materials.id("blue")),
        ("-x/20 + 0.5", materials.id("red"))
    ]
)
cube.set_attribute(pv.DefaultAttributes.VOLUME_FRACTIONS, fraction_gradient)
root = cube

voxel_size = pv.Vec3(0.0423, 0.0846, 0.027)
output_dir = os.path.join(os.path.dirname(__file__), "output")
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
    pvc.MaterialInkjetExportMode.STOCHASTIC,
)


def on_progress(p):
    print("compile progress: {:.1f}%".format(100.0 * p))


compiler.set_progress_callback(on_progress)
compiler.compile()
print("resolution (x, y, z png count):", compiler.resolution())
print("material voxel counts:", compiler.material_voxel_counts())

viz.Render(root, materials)
