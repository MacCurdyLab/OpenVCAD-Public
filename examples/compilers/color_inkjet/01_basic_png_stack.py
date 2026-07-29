"""
Color Inkjet — basic PNG stack
===============================

Builds a prism with a smooth **COLOR_RGBA** gradient, compiles a color-inkjet
PNG slice stack (full-color design → discrete ink assignments via the color
pipeline), then opens the interactive renderer.

Companion to: docs/source/guides/compilers/color-inkjet.md
"""
import os
import shutil

import pyvcad as pv
import pyvcad_compilers as pvc
import pyvcad_rendering as viz

materials = pv.default_materials

cube = pv.RectPrism(pv.Vec3(0, 0, 0), pv.Vec3(20, 10, 10))

# Green (left) to magenta (right) along X — same pattern as Getting Started Lesson 5
r_expr = "x/20 + 0.5"
g_expr = "-x/20 + 0.5"
b_expr = "x/20 + 0.5"
a_expr = "1.0"
color_gradient = pv.Vec4Attribute(r_expr, g_expr, b_expr, a_expr)
cube.set_attribute(pv.DefaultAttributes.COLOR_RGBA, color_gradient)

root = cube

voxel_size = pv.Vec3(0.15, 0.15, 0.15)
output_dir = os.path.join(os.path.dirname(__file__), "output")
prefix = "slice_"

if os.path.isdir(output_dir):
    shutil.rmtree(output_dir)
os.makedirs(output_dir, exist_ok=True)

compiler = pvc.ColorInkjetCompiler(root, voxel_size, output_dir, prefix, "default")


def on_progress(p):
    print("compile progress: {:.1f}%".format(100.0 * p))


compiler.set_progress_callback(on_progress)
compiler.compile()
print("resolution (x, y, z png count):", compiler.resolution())

viz.Render(root, materials)
