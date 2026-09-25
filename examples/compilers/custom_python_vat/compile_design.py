"""Compile the example exposure-gradient prism into grayscale PNG layers."""

from pathlib import Path

import pyvcad as pv

from design import build_design
from grayscale_vat_compiler import GrayscaleVatCompiler


root = build_design()

printer_size_mm = pv.Vec3(60.0, 40.0, 20.0)
dpi = 100.0
layer_height_mm = 1.0
output_directory = Path(__file__).parent / "output"

compiler = GrayscaleVatCompiler(
    root,
    printer_size_mm,
    dpi,
    layer_height_mm,
    output_directory,
)


def show_progress(percent):
    if percent % 10 == 0:
        print("Compiling: {:3d}%".format(percent))


layers = compiler.compile(show_progress)
print("Wrote {} layers to {}".format(len(layers), output_directory))
print("Image size: {} x {} pixels".format(
    compiler.image_width,
    compiler.image_height,
))
