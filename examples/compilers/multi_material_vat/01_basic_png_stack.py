"""
Multi-material VAT — basic two-material gradient
=================================================

Builds a rectangular prism with a red-to-blue material gradient, resolves its
volume fractions into synchronized Vat A and Vat B exposure masks, and opens
the interactive material preview. Both materials use full exposure because no
intensity attributes are assigned.
"""
import os
import shutil

import pyvcad as pv
import pyvcad_compilers as pvc
import pyvcad_rendering as viz

materials = pv.default_materials
red_id = materials.id("red")
blue_id = materials.id("blue")

root = pv.RectPrism.FromMinAndMax(
    pv.Vec3(-10.0, -5.0, 0.0),
    pv.Vec3(10.0, 5.0, 4.0),
)

# The fractions choose which vat owns each addressable pixel. They do not set
# exposure brightness directly.
root.set_attribute(
    pv.DefaultAttributes.VOLUME_FRACTIONS,
    pv.VolumeFractionsAttribute(
        [
            ("0.5 - x / 20", red_id),
            ("0.5 + x / 20", blue_id),
        ]
    ),
)

output_dir = os.path.join(os.path.dirname(__file__), "basic_output")
output_zip = output_dir + ".zip"
if os.path.isdir(output_dir):
    shutil.rmtree(output_dir)
if os.path.isfile(output_zip):
    os.remove(output_zip)

compiler = pvc.MultiMaterialVatCompiler(
    root,
    output_dir,
    materials,
    ["red", "blue"],
    layer_thickness=0.1,
    system=pvc.MultiMaterialVatSystem.DUAL,
    output_mode=pvc.MultiMaterialVatOutputMode.ZIP
)


def on_progress(progress):
    print("compile progress: {:.1f}%".format(100.0 * progress))


compiler.set_progress_callback(on_progress)
compiler.compile()
print("resolution (x, y, layers):", compiler.resolution())
print("directory:", output_dir)

viz.Render(root, materials)
