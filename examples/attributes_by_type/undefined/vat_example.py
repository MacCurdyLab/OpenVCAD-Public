"""
Undefined Attributes — VatCompiler
==================================

The VatCompiler generates grayscale BMP slice stacks driven by the INTENSITY
attribute. Every inside voxel needs an exposure intensity between 0 and 1, but
geometric combinations can still create regions where INTENSITY is undefined.

This example demonstrates three responses using two overlapping cubes where
only one child carries INTENSITY:

  1. Default mode: undefined voxels use the fallback intensity of 1.0.
  2. Custom fallback: the user overrides the fallback intensity.
  3. Strict mode: the compiler raises RuntimeError on the first undefined voxel.
"""
import os
import shutil

import pyvcad as pv
import pyvcad_compilers as pvc
import pyvcad_rendering as viz

left_cube = pv.RectPrism(pv.Vec3(-5, 0, 0), pv.Vec3(10, 10, 10))
right_cube = pv.RectPrism(pv.Vec3(5, 0, 0), pv.Vec3(10, 10, 10))

left_cube.set_attribute(pv.DefaultAttributes.INTENSITY, pv.FloatAttribute(0.25))

root = pv.Union(left_cube, right_cube)

voxel_size = pv.Vec3(0.5, 0.5, 0.5)
script_dir = os.path.dirname(os.path.abspath(__file__))
default_output_dir = os.path.join(script_dir, "vat_default")
custom_output_dir = os.path.join(script_dir, "vat_custom_fallback")
strict_output_dir = os.path.join(script_dir, "vat_strict")

for out_dir in (default_output_dir, custom_output_dir, strict_output_dir):
    if os.path.isdir(out_dir):
        shutil.rmtree(out_dir)
    os.makedirs(out_dir, exist_ok=True)

viz.Render(root)

compiler = pvc.VatCompiler(root, voxel_size, default_output_dir, "slice_")
compiler.compile()
print("1. Default mode completed — undefined region assigned fallback intensity 1.0")

compiler2 = pvc.VatCompiler(root, voxel_size, custom_output_dir, "slice_")
compiler2.set_fallback_intensity(0.6)
compiler2.compile()
print("2. Custom fallback completed — undefined region assigned fallback intensity 0.6")

compiler3 = pvc.VatCompiler(root, voxel_size, strict_output_dir, "slice_")
compiler3.set_strict_mode(True)

try:
    compiler3.compile()
except RuntimeError as e:
    print(f"3. Strict mode caught error:\n   {e}")
