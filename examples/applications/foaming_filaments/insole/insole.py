import pyvcad as pv
import pyvcad_attribute_resolver as resolver
import pyvcad_compilers as pvc
import pyvcad_rendering as viz
import shutil
from pathlib import Path

render = True
export = False

voxel_size = pv.Vec3(0.2,0.2,0.2)
j750_voxel_size = pv.Vec3(0.0423,0.0846,0.027)
j750_materials = pv.j750_materials

# Load Meshes
whole_insole = pv.Mesh("whole_insole.stl")
arch = pv.Mesh("arch.stl")
heal = pv.Mesh("heal.stl")
right = pv.Mesh("right.stl")
front = pv.Mesh("front.stl")
regions = pv.BBoxUnion([arch, heal, right, front])
extra_space = pv.Difference(whole_insole, regions)

# Shore Hardnesses
core_shore_hardness = 75.0
arch_shore_hardness = 85.0
heal_shore_hardness = 65.0
right_shore_hardness = 85.0
front_shore_hardness = 75.0

# Apply Attributes
whole_insole.set_attribute(pv.DefaultAttributes.SHORE_HARDNESS, pv.FloatAttribute(core_shore_hardness))
arch.set_attribute(pv.DefaultAttributes.SHORE_HARDNESS, pv.FloatAttribute(arch_shore_hardness))
heal.set_attribute(pv.DefaultAttributes.SHORE_HARDNESS, pv.FloatAttribute(heal_shore_hardness))
right.set_attribute(pv.DefaultAttributes.SHORE_HARDNESS, pv.FloatAttribute(right_shore_hardness))
front.set_attribute(pv.DefaultAttributes.SHORE_HARDNESS, pv.FloatAttribute(front_shore_hardness))

union = pv.BBoxUnion([arch, heal, right, front, extra_space])

blended = pv.Blend(union, [pv.DefaultAttributes.SHORE_HARDNESS], [7.0, 7.0, 7.0], num_passes=3, override_voxel_size=[voxel_size.x, voxel_size.y, voxel_size.z])
design_root = blended

# Target: foaming TPU on filament hardware -> temperature + flow_rate
resolver.clear_conversions()
resolver.register_tpu_conversions()
filament_root = resolver.adapt(
    design_root,
    ["temperature", "flow_rate"],
    tags=["foaming_tpu"],
)

# Target: J750 inkjet hardware -> volume_fractions
resolver.clear_conversions()
resolver.register_j750_shore_hardness_conversions(
    material_defs=pv.default_materials,
    agilus_material="black",
    vero_material="white",
)
j750_root = resolver.adapt(
    design_root,
    ["volume_fractions"],
    tags=["j750_shore_hardness"],
)

root = filament_root

if render:
    viz.Render(j750_root)

if export:
    here = Path(__file__).resolve().parent
    output_dir = here / "output"
    output_dir.mkdir(exist_ok=True)

    # The slicer backend needs process attributes instead of hardness directly.
    profiles_dir = here.parent / "profiles"
    printer_profile_path = profiles_dir / "prusa_mk4s_profile.ini"
    filament_profile_path = profiles_dir / "ColorFabb_VarioShore_TPU.ini"

    slicer_output_path = output_dir / "insole_foaming_filament.3mf"
    slicer_compiler = pvc.PrusaSlicerProjectCompiler(
        root,
        voxel_size,
        str(slicer_output_path),
        10,
        str(printer_profile_path),
        str(filament_profile_path),
    )
    slicer_compiler.compile()
    print("Wrote", slicer_output_path)

    # The inkjet backend consumes the resolved J750 material volume fractions.
    inkjet_output_dir = output_dir / "insole_j750_slices"
    if inkjet_output_dir.is_dir():
        shutil.rmtree(inkjet_output_dir)
    inkjet_output_dir.mkdir(exist_ok=True)

    inkjet_compiler = pvc.MaterialInkjetCompiler(
        j750_root,
        j750_voxel_size,
        str(inkjet_output_dir),
        "slice_",
        pv.default_materials,
        0.0,
    )
    inkjet_compiler.compile()
    print("Wrote", inkjet_output_dir)
