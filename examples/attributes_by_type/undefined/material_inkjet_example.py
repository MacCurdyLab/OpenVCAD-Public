"""
Undefined Attributes — MaterialInkjetCompiler
==============================================

The MaterialInkjetCompiler generates PNG slice stacks driven by volume fraction
attributes (VOLUME_FRACTIONS). Each inside voxel is stochastically assigned a
discrete material ID based on the volume fraction distribution at that point.

When a region of the design has geometry but no VOLUME_FRACTIONS attribute, the
compiler must decide how to handle the undefined material. OpenVCAD provides
three options, identical in spirit to the ColorInkjetCompiler:

  1. Default mode: undefined voxels receive a fallback material. The default
     fallback is material ID 0, which is conventionally the "void" material in
     the material definition file. This means the voxel is still marked as
     active but assigned to void — it will print as clear/support material.
  2. Custom fallback: the user overrides the fallback material ID. For example,
     setting it to red material ID would assign undefined regions to the red material
  3. Strict mode: the compiler raises a RuntimeError on the first voxel where
     VOLUME_FRACTIONS is missing, including the world-space XYZ location.

This example demonstrates all three using two overlapping cubes where only one
carries volume fractions.
"""
import pyvcad as pv
import pyvcad_compilers as pvc
import pyvcad_rendering as viz

materials = pv.default_materials

# ---- Build the design -------------------------------------------------------
# Two cubes in a Union. Only the left cube has volume fractions; the right
# cube's region will have no VOLUME_FRACTIONS, creating the undefined condition.

left_cube = pv.RectPrism(pv.Vec3(-5, 0, 0), pv.Vec3(10, 10, 10))
right_cube = pv.RectPrism(pv.Vec3(5, 0, 0), pv.Vec3(10, 10, 10))

# Assign 100% "green" material
vf = pv.VolumeFractionsAttribute([("1.0", materials.id("green"))])
left_cube.set_attribute(pv.DefaultAttributes.VOLUME_FRACTIONS, vf)

root = pv.Union(left_cube, right_cube)

voxel_size = pv.Vec3(0.5, 0.5, 0.5)

# Render the design to see the undefined region (gray stripes) when "volume_fractions" is the selected attribute
viz.Render(root, materials)

# ---- 1. Default mode --------------------------------------------------------
# No configuration needed. The undefined right cube is assigned to material 0
# (the void material) by default and the compile completes silently.

compiler = pvc.MaterialInkjetCompiler(
    root, voxel_size, "material_default", "slice_", materials)
compiler.compile()
print("1. Default mode completed — undefined region assigned to void (material 0)")

# ---- 2. Custom fallback material ID -----------------------------------------
# Override the fallback to red material so that undefined regions are assigned to
# the first real material instead of void.

compiler2 = pvc.MaterialInkjetCompiler(
    root, voxel_size, "material_custom_fallback", "slice_", materials)
compiler2.set_fallback_material_id(materials.id("red"))
compiler2.compile()
print("2. Custom fallback completed — undefined region assigned to red material")

# ---- 3. Strict mode ---------------------------------------------------------
# The compiler raises RuntimeError on the first voxel where VOLUME_FRACTIONS is
# undefined. Useful for catching design gaps before sending a job to the printer.

compiler3 = pvc.MaterialInkjetCompiler(
    root, voxel_size, "material_strict", "slice_", materials)
compiler3.set_strict_mode(True)

try:
    compiler3.compile()
except RuntimeError as e:
    print(f"3. Strict mode caught error:\n   {e}")
