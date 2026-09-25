"""
Multi-material VAT — four-material gradient
============================================

Builds a rectangular prism with red, green, blue, and yellow concentrated at
different XY corners. Bilinear volume-fraction weights create smooth mixtures
between all four corners, which a quad-vat compiler resolves into synchronized
Vat A through Vat D exposure masks.
"""
import os
import shutil

import pyvcad as pv
import pyvcad_compilers as pvc
import pyvcad_rendering as viz

materials = pv.default_materials
red_id = materials.id("red")
green_id = materials.id("green")
blue_id = materials.id("blue")
yellow_id = materials.id("yellow")

root = pv.RectPrism.FromMinAndMax(
    pv.Vec3(-10.0, -5.0, 0.0),
    pv.Vec3(10.0, 5.0, 4.0),
)

# Left/right and bottom/top weights each sum to one. Their products therefore
# form four nonnegative corner weights that also sum to one everywhere.
root.set_attribute(
    pv.DefaultAttributes.VOLUME_FRACTIONS,
    pv.VolumeFractionsAttribute(
        [
            ("((10 - x) / 20) * ((5 - y) / 10)", red_id),
            ("((10 + x) / 20) * ((5 - y) / 10)", green_id),
            ("((10 - x) / 20) * ((5 + y) / 10)", blue_id),
            ("((10 + x) / 20) * ((5 + y) / 10)", yellow_id),
        ]
    ),
)

output_dir = os.path.join(os.path.dirname(__file__), "four_material_output")
output_zip = output_dir + ".zip"
if os.path.isdir(output_dir):
    shutil.rmtree(output_dir)
if os.path.isfile(output_zip):
    os.remove(output_zip)

compiler = pvc.MultiMaterialVatCompiler(
    root,
    output_dir,
    materials,
    ["red", "green", "blue", "yellow"],
    layer_thickness=0.1,
    system=pvc.MultiMaterialVatSystem.QUAD,
    output_mode=pvc.MultiMaterialVatOutputMode.ZIP,
    random_seed=126,
)


def on_progress(progress):
    print("compile progress: {:.1f}%".format(100.0 * progress))


compiler.set_progress_callback(on_progress)
compiler.compile()
print("resolution (x, y, layers):", compiler.resolution())
print("archive:", compiler.archive_path())

viz.Render(root, materials)
