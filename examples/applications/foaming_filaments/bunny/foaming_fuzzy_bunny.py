from pathlib import Path

import pyvcad as pv
import pyvcad_compilers as pvc
import pyvcad_rendering as viz
import pyvcad_attribute_resolver as resolver

# Execution controls
render = False
export = True

enable_blending = True
enable_fuzzy_skin_attributes = True
enable_color_rgb_attributes = False

# Bunny mesh and final print scale
mesh_voxel_size = 0.20
model_scale = 1.2

# Fuzzy-skin regimes (mm)
high_fuzzy_skin_thickness = 0.5
high_fuzzy_skin_point_distance = 0.50
low_fuzzy_skin_thickness = 0.0
low_fuzzy_skin_point_distance = 1.0
long_hair_fuzzy_skin_thickness = high_fuzzy_skin_thickness
long_hair_fuzzy_skin_point_distance = 1.0

# Shore hardness regimes (Shore A)
stiff_shore_hardness = 85.0
soft_shore_hardness = 65.0

# Color-blind friendly RGB colors for visualizing each body/tool region
body_color_rgb = (0.34, 0.71, 0.91)
feet_color_rgb = (0.90, 0.60, 0.00)
ears_color_rgb = (0.00, 0.62, 0.45)
tail_color_rgb = (0.80, 0.47, 0.65)
eyes_color_rgb = (0.00, 0.00, 0.00)


# Attribute blending
blend_radius = 16.0
blend_passes = 3
blend_grid_voxel_size = 0.4

# PrusaSlicer project export
compiler_voxel_size = 0.25
num_regions = 6
output_directory_name = "output"
output_filename = "foaming_fuzzy_bunny.3mf"

here = Path(__file__).resolve().parent
bunny_path = here / "bunny_mesh.stl"


def set_fuzzy_skin(node, thickness, point_distance):
    if not enable_fuzzy_skin_attributes:
        return

    node.set_attribute(
        pv.DefaultAttributes.FUZZY_SKIN_THICKNESS,
        pv.FloatAttribute(thickness),
    )
    node.set_attribute(
        pv.DefaultAttributes.FUZZY_SKIN_POINT_DISTANCE,
        pv.FloatAttribute(point_distance),
    )

def set_shore_hardness(node, shore_hardness):
    node.set_attribute(
        pv.DefaultAttributes.SHORE_HARDNESS,
        pv.FloatAttribute(shore_hardness),
    )

def set_color_rgb(node, color_rgb):
    if not enable_color_rgb_attributes:
        return

    node.set_attribute(
        pv.DefaultAttributes.COLOR_RGB,
        pv.Vec3Attribute(color_rgb[0], color_rgb[1], color_rgb[2]),
    )

def get_blend_attributes():
    attributes = [
        pv.DefaultAttributes.SHORE_HARDNESS,
    ]

    if enable_fuzzy_skin_attributes:
        attributes = [
            pv.DefaultAttributes.FUZZY_SKIN_THICKNESS,
            pv.DefaultAttributes.FUZZY_SKIN_POINT_DISTANCE,
        ] + attributes

    if enable_color_rgb_attributes:
        attributes.append(pv.DefaultAttributes.COLOR_RGB)

    return attributes

# The source mesh is upright, about 86 x 67 x 83 mm, with the nose toward -X.
# It contains open edges, so validation is intentionally disabled.
bunny = pv.Mesh(
    str(bunny_path),
    center=False,
    disable_validation=True,
    override_voxel_size=mesh_voxel_size,
)
set_fuzzy_skin(
    bunny,
    high_fuzzy_skin_thickness,
    high_fuzzy_skin_point_distance,
)
set_shore_hardness(
    bunny,
    stiff_shore_hardness,
)
set_color_rgb(
    bunny,
    body_color_rgb,
)

# Define region for feet
feet_tool = pv.RectPrism.FromMinAndMax(
    pv.Vec3(-50.0, -40.0, 0.0),
    pv.Vec3(50.0, 40.0, 20.0),
)
feet_region = pv.Intersection(bunny, feet_tool)
set_fuzzy_skin(
    feet_region,
    low_fuzzy_skin_thickness,
    low_fuzzy_skin_point_distance,
)
set_shore_hardness(
    feet_region,
    stiff_shore_hardness,
)
set_color_rgb(
    feet_region,
    feet_color_rgb,
)

# Define Region for Ears
ears_tool = pv.RectPrism.FromMinAndMax(
    pv.Vec3(-40.0, -50.0, 62.0),
    pv.Vec3(40.0, 50.0, 90.0),
)
ears_region = pv.Intersection(bunny, ears_tool)
set_fuzzy_skin(
    ears_region,
    low_fuzzy_skin_thickness,
    low_fuzzy_skin_point_distance,
)
set_shore_hardness(
    ears_region,
    soft_shore_hardness,
)
set_color_rgb(
    ears_region,
    ears_color_rgb,
)

# Define Region for Tail
tail_tool = pv.RectPrism.FromMinAndMax(
    pv.Vec3(30.0, -30.0, 0.0),
    pv.Vec3(45.0, 30.0, 22.0),
)
tail_region = pv.Intersection(bunny, tail_tool)
set_fuzzy_skin(
    tail_region,
    long_hair_fuzzy_skin_thickness,
    long_hair_fuzzy_skin_point_distance,
)
set_shore_hardness(
    tail_region,
    soft_shore_hardness,
)
set_color_rgb(
    tail_region,
    tail_color_rgb,
)


bunny = pv.Union(feet_region, bunny)
bunny = pv.Union(ears_region, bunny)

if enable_blending:
    bunny = pv.Blend(
        bunny,
        get_blend_attributes(),
        [blend_radius, blend_radius, blend_radius],
        num_passes=blend_passes,
        override_voxel_size=[
            blend_grid_voxel_size,
            blend_grid_voxel_size,
            blend_grid_voxel_size,
        ],
    )

# Apply the eyes after blending so their nearly smooth texture has a discrete edge
eye_tools = pv.BBoxUnion([
    pv.Sphere(pv.Vec3(-27.0, -16.0, 59.0), 6.25),
    pv.Sphere(pv.Vec3(-38.0, -12.0, 58.0), 4.5),
])
eyes_region = pv.Intersection(bunny, eye_tools)
set_fuzzy_skin(
    eyes_region,
    low_fuzzy_skin_thickness,
    low_fuzzy_skin_point_distance,
)
set_shore_hardness(
    eyes_region,
    soft_shore_hardness,
)
set_color_rgb(
    eyes_region,
    eyes_color_rgb,
)

bunny = pv.Union(tail_region, bunny)
if enable_blending:
    bunny = pv.Blend(
        bunny,
        get_blend_attributes(),
        [4, 4, 4],
        num_passes=blend_passes,
        override_voxel_size=[
            blend_grid_voxel_size,
            blend_grid_voxel_size,
            blend_grid_voxel_size,
        ],
    )
bunny = pv.Union(eyes_region, bunny)

# Target: foaming TPU on filament hardware -> temperature + flow_rate
resolver.clear_conversions()
resolver.register_tpu_conversions()
bunny = resolver.adapt(
    bunny,
    ["temperature", "flow_rate"],
    tags=["foaming_tpu"],
)

root = bunny
root = pv.Scale(model_scale,root)

if render:
    viz.Render(root)

if export:
    output_dir = here / output_directory_name
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / output_filename

    # The slicer backend needs process attributes instead of hardness directly.
    profiles_dir = here.parent / "profiles"
    printer_profile_path = profiles_dir / "prusa_mk4s_profile.ini"
    filament_profile_path = profiles_dir / "ColorFabb_VarioShore_TPU.ini"

    compiler = pvc.PrusaSlicerProjectCompiler(
        root,
        pv.Vec3(
            compiler_voxel_size,
            compiler_voxel_size,
            compiler_voxel_size,
        ),
        str(output_path),
        num_regions,
        str(printer_profile_path),
        str(filament_profile_path),
    )

    def report_progress(progress):
        print(f"Slicer export progress: {progress * 100:.1f}%")

    compiler.set_progress_callback(report_progress)
    compiler.compile()
    print("Wrote", output_path)
    if enable_fuzzy_skin_attributes:
        print("Enable fuzzy skin for Outside walls when opening the project in PrusaSlicer.")
