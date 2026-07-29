"""
VAT Photo — basic BMP stack
===========================

Builds a prism with a smooth scalar INTENSITY gradient, compiles a grayscale
BMP slice stack on a fixed printer-volume canvas for vat-photo style printers,
then opens the interactive preview.
"""
import os
import shutil

import pyvcad as pv
import pyvcad_compilers as pvc
import pyvcad_rendering as viz

cube = pv.RectPrism(pv.Vec3(0, 0, 0), pv.Vec3(20, 10, 10))

# High exposure on the left, low exposure on the right so the exported
# bitmaps show a visible grayscale ramp after the X-axis image flip.
intensity_gradient = pv.FloatAttribute("-x/20 + 0.5")
cube.set_attribute(pv.DefaultAttributes.INTENSITY, intensity_gradient)

root = cube

voxel_size = pv.Vec3(0.15, 0.15, 0.15)
printer_volume = pv.Vec3(96.0, 54.0, 100.0)
output_dir = os.path.join(os.path.dirname(__file__), "output")
prefix = "slice_"

if os.path.isdir(output_dir):
    shutil.rmtree(output_dir)
os.makedirs(output_dir, exist_ok=True)

compiler = pvc.VatCompiler(root, voxel_size, printer_volume, output_dir, prefix)


def on_progress(p):
    print("compile progress: {:.1f}%".format(100.0 * p))


compiler.set_progress_callback(on_progress)
compiler.compile()
print("resolution (x, y, z bmp count):", compiler.resolution())

viz.Render(root)
