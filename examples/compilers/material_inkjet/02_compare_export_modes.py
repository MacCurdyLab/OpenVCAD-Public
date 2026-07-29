"""
Material Inkjet - stochastic vs 3D error-diffused comparison
============================================================

Compiles the same uniform 50/50 red-blue volume-fraction mixture with both
material assignment modes so their voxel patterns and material counts can be
compared directly.
"""
from pathlib import Path
import shutil

import pyvcad as pv
import pyvcad_compilers as pvc
import pyvcad_rendering as viz


materials = pv.default_materials
red_id = materials.id("red")
blue_id = materials.id("blue")

root = pv.RectPrism(
    pv.Vec3(0.0, 0.0, 0.0),
    pv.Vec3(16.0, 16.0, 4.0),
)
root.set_attribute(
    pv.DefaultAttributes.VOLUME_FRACTIONS,
    pv.VolumeFractionsAttribute(
        [
            (0.5, red_id),
            (0.5, blue_id),
        ]
    ),
)

voxel_size = pv.Vec3(0.25, 0.25, 0.25)
prefix = "slice_"
script_dir = Path(__file__).resolve().parent
output_root = script_dir / "output"
stochastic_output_dir = output_root / "stochastic"
dithered_output_dir = output_root / "dithered_3d"

if output_root.is_dir():
    shutil.rmtree(output_root)
stochastic_output_dir.mkdir(parents=True)
dithered_output_dir.mkdir(parents=True)

stochastic_compiler = pvc.MaterialInkjetCompiler(
    root,
    voxel_size,
    str(stochastic_output_dir),
    prefix,
    materials,
    0.0,
    pvc.MaterialInkjetExportMode.STOCHASTIC,
)
stochastic_compiler.compile()
stochastic_counts = stochastic_compiler.material_voxel_counts()

dithered_compiler = pvc.MaterialInkjetCompiler(
    root,
    voxel_size,
    str(dithered_output_dir),
    prefix,
    materials,
    0.0,
    pvc.MaterialInkjetExportMode.DITHERED_3D,
)
dithered_compiler.compile()
dithered_counts = dithered_compiler.material_voxel_counts()

print("stochastic material voxel counts:", stochastic_counts)
print("dithered material voxel counts:", dithered_counts)

viz.Render(root, materials)
