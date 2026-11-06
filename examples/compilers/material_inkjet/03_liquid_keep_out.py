"""
Material Inkjet - liquid keep-out
=================================

Compiles a red / liquid / support mixture three times to show how liquid
keep-out clears materials from a band just inside the part surface:

1. No keep-out: every material appears all the way to the surface.
2. Default keep-out: the material named "liquid" (or "M.Cleanser") is removed
   within liquid_keep_out_distance of the surface.
3. Custom keep-out list: set_liquid_keep_out_materials() names any number of
   materials to remove instead. The list replaces the default, so "liquid" is
   included again here alongside "support".

Companion to: docs/source/guides/compilers/material-inkjet.md
"""
from pathlib import Path
import shutil

import pyvcad as pv
import pyvcad_compilers as pvc
import pyvcad_rendering as viz


materials = pv.default_materials
red_id = materials.id("red")
liquid_id = materials.id("liquid")
support_id = materials.id("support")

root = pv.RectPrism(
    pv.Vec3(0.0, 0.0, 0.0),
    pv.Vec3(12.0, 12.0, 4.0),
)
root.set_attribute(
    pv.DefaultAttributes.VOLUME_FRACTIONS,
    pv.VolumeFractionsAttribute(
        [
            (0.4, red_id),
            (0.3, liquid_id),
            (0.3, support_id),
        ]
    ),
)

voxel_size = pv.Vec3(0.1, 0.1, 0.1)
keep_out_distance = 1.5  # mm inside the surface
prefix = "slice_"
script_dir = Path(__file__).resolve().parent
output_root = script_dir / "output" / "liquid_keep_out"
no_keep_out_dir = output_root / "no_keep_out"
default_keep_out_dir = output_root / "default_keep_out"
custom_keep_out_dir = output_root / "custom_keep_out"

if output_root.is_dir():
    shutil.rmtree(output_root)
for directory in (no_keep_out_dir, default_keep_out_dir, custom_keep_out_dir):
    directory.mkdir(parents=True)


def compile_stack(output_dir, distance, keep_out_materials=None):
    # Keep-out is a hard constraint in both export modes; DITHERED_3D keeps
    # the output deterministic between runs.
    compiler = pvc.MaterialInkjetCompiler(
        root,
        voxel_size,
        str(output_dir),
        prefix,
        materials,
        distance,
        pvc.MaterialInkjetExportMode.DITHERED_3D,
    )
    if keep_out_materials is not None:
        compiler.set_liquid_keep_out_materials(keep_out_materials)
    compiler.compile()
    return {materials.name(material_id): count
            for material_id, count in compiler.material_voxel_counts().items()}


# 1. Keep-out disabled.
no_keep_out_counts = compile_stack(no_keep_out_dir, 0.0)

# 2. Default keep-out removes only "liquid" near the surface.
default_keep_out_counts = compile_stack(default_keep_out_dir, keep_out_distance)

# 3. Custom keep-out removes every listed material near the surface.
custom_keep_out_counts = compile_stack(custom_keep_out_dir, keep_out_distance, ["liquid", "support"])

print("no keep-out:     ", no_keep_out_counts)
print("default keep-out:", default_keep_out_counts)
print("custom keep-out: ", custom_keep_out_counts)

viz.Render(root, materials)
