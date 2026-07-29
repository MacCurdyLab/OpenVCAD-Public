"""
Undefined Attributes — ColorInkjetCompiler
==========================================

In OpenVCAD's attribute modeling system, every region of a design can carry
continuous attribute fields (color, material fractions, mechanical properties,
etc.). When multiple geometries are combined via Union, it is possible for some
regions to end up without a required attribute — for example, one child has a
COLOR_RGBA attribute and the other does not.

This becomes a problem at compile time. The ColorInkjetCompiler needs a color
value for every voxel that lies inside the compiled domain. If a voxel has no
COLOR_RGBA attribute, the compiler must decide what to do.

OpenVCAD provides three options:
  1. Default mode (no flags needed): undefined regions silently receive a
     fallback color (fully transparent RGBA 0,0,0,0 by default).
  2. Custom fallback: the user overrides the fallback color to a specific value.
  3. Strict mode: the compiler raises a RuntimeError on the first undefined
     voxel, reporting the world-space XYZ so the user can locate and fix the
     gap in their design.

This example demonstrates all three using two overlapping cubes where only one
carries a COLOR_RGBA attribute.
"""
import pyvcad as pv
import pyvcad_compilers as pvc
import pyvcad_rendering as viz

# ---- Build the design -------------------------------------------------------
# Two cubes in a Union. Only the left cube has a color; the right cube's region
# will have no COLOR_RGBA attribute, creating the "undefined" condition.

left_cube = pv.RectPrism(pv.Vec3(-5, 0, 0), pv.Vec3(10, 10, 10))
right_cube = pv.RectPrism(pv.Vec3(5, 0, 0), pv.Vec3(10, 10, 10))

red = pv.Vec4Attribute("1.0", "0.0", "0.0", "1.0")
left_cube.set_attribute(pv.DefaultAttributes.COLOR_RGBA, red)

root = pv.Union(left_cube, right_cube)

voxel_size = pv.Vec3(0.5, 0.5, 0.5)

# Render the design to see the undefined region (gray stripes) when "color_rgba" is the selected attribute
viz.Render(root)

# ---- 1. Default mode --------------------------------------------------------
# No extra configuration needed. The compiler uses a fully transparent fallback
# (RGBA 0,0,0,0) for the undefined right cube and completes without error.

compiler = pvc.ColorInkjetCompiler(root, voxel_size, "color_default", "slice_")
compiler.compile()
print("1. Default mode completed — undefined region treated as transparent (0,0,0,0)")

# ---- 2. Custom fallback color -----------------------------------------------
# Override the fallback to solid green so undefined regions print as green
# instead of transparent.

compiler2 = pvc.ColorInkjetCompiler(root, voxel_size, "color_custom_fallback", "slice_")
compiler2.set_fallback_color(pv.Vec4(0.0, 1.0, 0.0, 1.0))
compiler2.compile()
print("2. Custom fallback completed — undefined region treated as green (0,1,0,1)")

# ---- 3. Strict mode ---------------------------------------------------------
# Enable strict mode so the compiler raises a RuntimeError instead of using any
# fallback. This is useful during development to find gaps in the design.

compiler3 = pvc.ColorInkjetCompiler(root, voxel_size, "color_strict", "slice_")
compiler3.set_strict_mode(True)

try:
    compiler3.compile()
except RuntimeError as e:
    print(f"3. Strict mode caught error:\n   {e}")
