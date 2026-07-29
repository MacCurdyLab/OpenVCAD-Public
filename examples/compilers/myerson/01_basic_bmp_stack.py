"""
Myerson — basic BMP stack
=========================

Builds a prism centered at the origin with a horizontal VOLUME_FRACTIONS
gradient that is 100% red at the negative-X end and 100% blue at the
positive-X end, then exports legacy Myerson-style per-material 1-bit BMP
stacks with fixed-width centering and Y padding from taper/extra-width
settings.
"""
import os
import shutil

import pyvcad as pv
import pyvcad_compilers as pvc
import pyvcad_rendering as viz

materials = pv.default_materials

# RectPrism takes (center, size), so keep the bar centered at the origin.
prism = pv.RectPrism(pv.Vec3(0, 0, 0), pv.Vec3(20, 10, 2))
fraction_gradient = pv.VolumeFractionsAttribute(
    [
        ("-x/20 + 0.5", materials.id("red")),
        ("x/20 + 0.5", materials.id("blue"))
    ]
)
prism.set_attribute(pv.DefaultAttributes.VOLUME_FRACTIONS, fraction_gradient)

root = prism

output_dir = os.path.join(os.path.dirname(__file__), "output")
if os.path.isdir(output_dir):
    shutil.rmtree(output_dir)
os.makedirs(output_dir, exist_ok=True)

compiler = pvc.MyersonCompiler(
    0.032,
    600,
    600,
    6.0,
    0.4,
    output_dir,
    root,
    materials
)


def on_progress(p):
    print("compile progress: {:.1f}%".format(100.0 * p))


compiler.set_progress_callback(on_progress)
compiler.compile()
print("resolution (width, height, bmp count):", compiler.resolution())

viz.Render(root, materials)
