"""
Multi-material VAT — independent two-material intensity
========================================================

Builds a red-to-blue rectangular prism and independently controls the exposure
intensity of both materials. Red brightens toward positive Y while blue dims
in the same direction. The volume fractions still determine which vat owns
each pixel; the intensity attributes only control selected-pixel brightness.
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
root.set_attribute(
    pv.DefaultAttributes.VOLUME_FRACTIONS,
    pv.VolumeFractionsAttribute(
        [
            ("0.5 - x / 20", red_id),
            ("0.5 + x / 20", blue_id),
        ]
    ),
)

# These named channels are sampled only after their material wins the
# stochastic volume-fraction selection at a pixel.
root.set_attribute("red_intensity", pv.FloatAttribute("0.2 + 0.8 * (y + 5) / 10"))
root.set_attribute("blue_intensity", pv.FloatAttribute("1.0 - 0.8 * (y + 5) / 10"))

output_dir = os.path.join(os.path.dirname(__file__), "intensity_output")
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
    output_mode=pvc.MultiMaterialVatOutputMode.DIRECTORY_AND_ZIP,
    random_seed=84,
)


def on_progress(progress):
    print("compile progress: {:.1f}%".format(100.0 * progress))


compiler.set_progress_callback(on_progress)
compiler.compile()
print("resolution (x, y, layers):", compiler.resolution())
print("directory:", output_dir)
print("archive:", compiler.archive_path())

viz.Render(root, materials)
