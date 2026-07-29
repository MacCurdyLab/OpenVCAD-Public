import math

import pyvcad as pv
import pyvcad_medical as med
import pyvcad_compilers as pvc
import pyvcad_rendering as viz

# Configuration
use_mesh = True
render = True
export = False
section_mode = "pie_1_3"  # "whole", "top", "bottom", "pie_3_4", "pie_1_3"
voxel_size = pv.Vec3(0.0423,0.0846,0.027)
scale = 0.21
prefix = "pumpkin_"
path = "dicom"
mesh_path = "mesh.stl"
output_dir = f"output/pumpkin_{round(scale*100)}_{section_mode}/"

pie_section_fractions = {
    "pie_3_4": 3.0 / 4.0,
    "pie_1_3": 1.0 / 3.0,
    "pie_3": 1.0 / 3.0,
}
valid_section_modes = ["whole", "top", "bottom"] + list(pie_section_fractions.keys())
if section_mode not in valid_section_modes:
    raise ValueError(f"section_mode must be one of: {', '.join(valid_section_modes)}")


def make_axis_halfspace(angle_degrees, center, x_size, clip_depth):
    clip = pv.RectPrism(pv.Vec3(0,0,0), pv.Vec3(x_size, clip_depth, 2.0 * clip_depth))
    clip = pv.Rotate(angle_degrees,0,0, clip)

    angle_radians = math.radians(-angle_degrees)
    normal_y = math.cos(angle_radians)
    normal_z = math.sin(angle_radians)

    return pv.Translate(
        center.x,
        center.y + normal_y * clip_depth / 2.0,
        center.z + normal_z * clip_depth / 2.0,
        clip
    )


def make_axis_wedge(angle_degrees, center, x_size, clip_depth):
    upper_halfspace = make_axis_halfspace(angle_degrees / 2.0, center, x_size, clip_depth)
    lower_halfspace = make_axis_halfspace(-angle_degrees / 2.0, center, x_size, clip_depth)
    return pv.Intersection(upper_halfspace, lower_halfspace)


def make_bbox_clip(bbox_min, bbox_max, margin):
    return pv.RectPrism.FromMinAndMax(
        pv.Vec3(bbox_min.x - margin, bbox_min.y - margin, bbox_min.z - margin),
        pv.Vec3(bbox_max.x + margin, bbox_max.y + margin, bbox_max.z + margin)
    )

# Build HU color map with sigmoid opacity
opacity_function = lambda t: med.color_maps.sigmoid_opacity_base(t, k=9.0, x0=0.2)
hu_color_map=med.color_maps.create_linear_gradient_hu_map(100, 255, palette=med.color_maps.get_color_palette("rainbow"), steps=30, opacity_function=opacity_function)

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

# Lay the object flat on the build plate while preserving the longest axis along X.
object = pv.Rotate(90,0,0, object)
object = pv.Scale(scale, object)

if section_mode in ["top", "bottom"]:
    section_bbox_min, section_bbox_max = object.bounding_box()
    section_y = (section_bbox_min.y + section_bbox_max.y) / 2

    if section_mode == "top":
        section_clip = pv.RectPrism.FromMinAndMax(
            pv.Vec3(section_bbox_min.x, section_y, section_bbox_min.z),
            pv.Vec3(section_bbox_max.x, section_bbox_max.y, section_bbox_max.z)
        )
        cut_face_down_pitch = -90
    else:
        section_clip = pv.RectPrism.FromMinAndMax(
            pv.Vec3(section_bbox_min.x, section_bbox_min.y, section_bbox_min.z),
            pv.Vec3(section_bbox_max.x, section_y, section_bbox_max.z)
        )
        cut_face_down_pitch = 90

    object = pv.Intersection(object, section_clip)
    object = pv.Rotate(cut_face_down_pitch,0,0, object)

if section_mode in pie_section_fractions:
    section_bbox_min, section_bbox_max = object.bounding_box()
    section_center = pv.Vec3(
        (section_bbox_min.x + section_bbox_max.x) / 2,
        (section_bbox_min.y + section_bbox_max.y) / 2,
        (section_bbox_min.z + section_bbox_max.z) / 2
    )
    section_size_x = section_bbox_max.x - section_bbox_min.x
    section_size_y = section_bbox_max.y - section_bbox_min.y
    section_size_z = section_bbox_max.z - section_bbox_min.z
    section_cross_section = math.sqrt(section_size_y * section_size_y + section_size_z * section_size_z)
    section_margin = section_cross_section * 0.05 + max(voxel_size.x, voxel_size.y, voxel_size.z) * 2.0
    clip_depth = section_cross_section + section_margin * 2.0
    x_size = section_size_x + section_margin * 2.0
    pie_fraction = pie_section_fractions[section_mode]
    pie_angle_degrees = 360.0 * pie_fraction

    if pie_fraction <= 0.5:
        pie_clip = make_axis_wedge(pie_angle_degrees, section_center, x_size, clip_depth)
        object = pv.Intersection(object, pie_clip)
    else:
        missing_angle_degrees = 360.0 * (1.0 - pie_fraction)
        full_clip = make_bbox_clip(section_bbox_min, section_bbox_max, section_margin)
        missing_wedge = make_axis_wedge(missing_angle_degrees, section_center, x_size, clip_depth)
        pie_clip = pv.Difference(full_clip, missing_wedge)
        object = pv.Intersection(object, pie_clip)

if section_mode != "whole":
    section_bbox_min, section_bbox_max = object.bounding_box()
    section_center = pv.Vec3(
        (section_bbox_min.x + section_bbox_max.x) / 2,
        (section_bbox_min.y + section_bbox_max.y) / 2,
        (section_bbox_min.z + section_bbox_max.z) / 2
    )
    object = pv.Translate(-section_center.x,-section_center.y,-section_center.z, object)

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
