import pyvcad as pv
import pyvcad_medical as med
import pyvcad_compilers as pvc
import pyvcad_rendering as viz

# Configuration
use_mesh = True
render = True
export = False
voxel_size = pv.Vec3(0.0423,0.0846,0.027)
scale = 0.32
prefix = "snes_"
path = "dicom"
mesh_path = "mesh.stl"
output_dir = f"output/snes_{round(scale*100)}/"

# Build a custom opacity profile over a configurable HU window. Values outside
# this lookup-table span receive no color entry and therefore stay transparent.
buttons_hu_min = 8.70
buttons_hu_max = 11.04
pcb_hu_min = 11.04
pcb_hu_max = 12.3
case_hu_min = 12.3
case_hu_max = 17.0
metal_hu_min = 17.0
metal_hu_max = 40.0

object_hu_min = buttons_hu_min
object_hu_max = metal_hu_max

buttons_opacity = 0.15
pcb_opacity = 0.02
case_opacity = 0.005
metal_opacity = 1.0
hu_color_map_steps = 512

opacity_regions = [
    ("buttons", buttons_hu_min, buttons_hu_max, buttons_opacity),
    ("pcb", pcb_hu_min, pcb_hu_max, pcb_opacity),
    ("case", case_hu_min, case_hu_max, case_opacity),
    ("metal", metal_hu_min, metal_hu_max, metal_opacity),
]

if object_hu_min >= object_hu_max:
    raise ValueError("object_hu_min must be less than object_hu_max")

for region_name, region_min, region_max, _ in opacity_regions:
    if region_min >= region_max:
        raise ValueError(f"{region_name} HU range must have min < max")

if opacity_regions[0][1] < object_hu_min:
    raise ValueError("The first opacity region starts below object_hu_min")

if opacity_regions[-1][2] > object_hu_max:
    raise ValueError("The last opacity region ends above object_hu_max")

for i in range(1, len(opacity_regions)):
    previous_name, _, previous_max, _ = opacity_regions[i - 1]
    region_name, region_min, _, _ = opacity_regions[i]
    if region_min < previous_max:
        raise ValueError(f"{region_name} overlaps {previous_name}")


def normalized_t_to_hu(t):
    t = max(0.0, min(1.0, t))
    return med.color_maps.lerp(object_hu_min, object_hu_max, t)


def opacity_function(t):
    hu = normalized_t_to_hu(t)

    for index, (_, region_min, region_max, opacity) in enumerate(opacity_regions):
        is_last_region = index == len(opacity_regions) - 1
        if is_last_region:
            if region_min <= hu <= region_max:
                return opacity
        else:
            if region_min <= hu < region_max:
                return opacity

    return 0.0


hu_color_map = med.color_maps.create_linear_gradient_hu_map(
    object_hu_min,
    object_hu_max,
    palette=med.color_maps.get_color_palette("rainbow"),
    steps=hu_color_map_steps,
    opacity_function=opacity_function,
)

# Load DICOM series
dicom_loader = pv.DICOMLoader(path)
med.imaging.print_loaded_dicom_info(dicom_loader)

# Convert to volume and attribute
dicom_volume = dicom_loader.as_volume()
dicom_attribute = pv.FloatAttribute(dicom_volume)

if use_mesh:
    object = pv.Mesh(mesh_path,disable_validation=True,compensate_slicer_ras=True)
else:
    volume_bbox_min, volume_bbox_max = dicom_volume.bounding_box()
    object = pv.RectPrism.FromMinAndMax(volume_bbox_min, pv.Vec3(volume_bbox_max.x, volume_bbox_max.y, volume_bbox_max.z))

object.set_attribute(pv.DefaultAttributes.HU, dicom_attribute)

mod = pv.LookupTableConverter([pv.DefaultAttributes.HU], [pv.DefaultAttributes.COLOR_RGBA], hu_color_map, pv.InterpolationMode.STEP)
object = pv.AttributeModifier(mod, object)

model_bbox_min, model_bbox_max = object.bounding_box()
model_center = pv.Vec3(
    (model_bbox_min.x + model_bbox_max.x) / 2,
    (model_bbox_min.y + model_bbox_max.y) / 2,
    (model_bbox_min.z + model_bbox_max.z) / 2
)
object = pv.Translate(-model_center.x,-model_center.y,-model_center.z, object)

# Lay the controller flat on the build plate with its longest bbox dimension along X.
object = pv.Rotate(-60,0,0, object)
object = pv.Scale(scale, object)

# Print final bounding box size (after scaling)
final_bbox_min, final_bbox_max = object.bounding_box()
print(f"Final Model BBox Size (mm): {final_bbox_max.x - final_bbox_min.x:.2f} x {final_bbox_max.y - final_bbox_min.y:.2f} x {final_bbox_max.z - final_bbox_min.z:.2f}")
print(f"Final Model BBox Center (mm): {(final_bbox_max.x + final_bbox_min.x) / 2:.2f}, {(final_bbox_max.y + final_bbox_min.y) / 2:.2f}, {(final_bbox_max.z + final_bbox_min.z) / 2:.2f}")

if render:
    viz.Render(object)

if export:
    print(f"Output Directory: {output_dir}")

    # Delete the output directory if it already exists
    import shutil, os
    if export and os.path.exists(output_dir):
        shutil.rmtree(output_dir)

    #Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    compiler = pvc.ColorInkjetCompiler(object, voxel_size, output_dir, prefix)

    def print_progress(progress):
        print(f"Compilation progress: {progress*100:.2f}%")

    compiler.set_progress_callback(print_progress)
    compiler.compile()
