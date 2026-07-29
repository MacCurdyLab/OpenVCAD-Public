"""
VAT Photo — bounding-box BMP stack
==================================

Builds the same prism and INTENSITY gradient as the printer-volume example,
but compiles only the model bounding box instead of a fixed printer canvas.
"""
import os
import shutil

import pyvcad as pv
import pyvcad_compilers as pvc
import pyvcad_rendering as viz

cube = pv.RectPrism(pv.Vec3(0, 0, 0), pv.Vec3(20, 10, 10))

# Same gradient as 01_basic_bmp_stack.py so the resulting slices can be
# compared directly against printer-volume mode.
intensity_gradient = pv.FloatAttribute("-x/20 + 0.5")
cube.set_attribute(pv.DefaultAttributes.INTENSITY, intensity_gradient)

root = cube

voxel_size = pv.Vec3(0.15, 0.15, 0.15)
output_dir = os.path.join(os.path.dirname(__file__), "output_bbox")
prefix = "slice_"

if os.path.isdir(output_dir):
    shutil.rmtree(output_dir)
os.makedirs(output_dir, exist_ok=True)

compiler = pvc.VatCompiler(root, voxel_size, output_dir, prefix)


def on_progress(p):
    print("compile progress: {:.1f}%".format(100.0 * p))


compiler.set_progress_callback(on_progress)
compiler.compile()
print("resolution (x, y, z bmp count):", compiler.resolution())

viz.Render(root)
