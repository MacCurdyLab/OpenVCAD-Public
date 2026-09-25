import pyvcad as pv
import pyvcad_medical as med
import pyvcad_compilers as pvc
import pyvcad_rendering as viz

mode = "right"
render = True
export = False
voxel_size = pv.Vec3(0.0423,0.0846,0.027)
scale = 0.7
color_palette = "cividis"
path = "dicom"
mesh_path = "MRTumor.stl"
output_dir = f"output/tumor_{mode}_{color_palette}_{round(scale*100)}/"
prefix = "tumor_"

# Build HU color map with opacity function
opacity_function = lambda t: 0.6 * (1 - t) + 0.15 * t # Create an opacity function that decreases linearly from 0.6 to 0.15
hu_color_map=med.color_maps.create_linear_gradient_hu_map(75, 190, palette=med.color_maps.get_color_palette(color_palette), steps=30, opacity_function=opacity_function)

# Load DICOM series
dicom_loader = pv.DICOMLoader(path)
med.imaging.print_loaded_dicom_info(dicom_loader)

# Convert to volume and attribute
dicom_volume = dicom_loader.as_volume()
dicom_attribute = pv.FloatAttribute(dicom_volume)

# Build object
head_mesh = pv.Mesh(mesh_path)
head_mesh.set_attribute(pv.DefaultAttributes.HU, pv.FloatAttribute(-2000))
head_mesh_offset = pv.Offset(-11, pv.Mesh(mesh_path))
head_mesh_offset.set_attribute(pv.DefaultAttributes.HU, dicom_attribute)
head_with_void = pv.Difference(head_mesh, head_mesh_offset)
head_union = pv.Union(head_with_void, head_mesh_offset)

# Apply HU to color conversion
mod = pv.LookupTableConverter([pv.DefaultAttributes.HU], [pv.DefaultAttributes.COLOR_RGBA], hu_color_map, pv.InterpolationMode.STEP)
attr_mod = pv.AttributeModifier(mod, head_union)

# Apply scaling
root = pv.Scale(scale, attr_mod)

# Clip to one hemisphere if specified
if mode != "whole":
    sign = 1 if mode == "right" else -1
    bbox_min, bbox_max = root.bounding_box()
    size = pv.Vec3((bbox_max.x - bbox_min.x)/2, bbox_max.y - bbox_min.y, bbox_max.z - bbox_min.z)
    rect_prism = pv.RectPrism(pv.Vec3(sign*(bbox_max.x - bbox_min.x)/4,0,0), size)
    root = pv.Intersection(root,rect_prism)

# Rotate for printer orientation
root = pv.Rotate(0,0, -90, root)

# Print final bounding box size (after scaling)
final_bbox_min, final_bbox_max = root.bounding_box()
print(f"Final Model BBox Size (mm): {final_bbox_max.x - final_bbox_min.x:.2f} x {final_bbox_max.y - final_bbox_min.y:.2f} x {final_bbox_max.z - final_bbox_min.z:.2f}")

if render:
    viz.Render(root)

if export:
    print(f"Output Directory: {output_dir}")

    # Delete the output directory if it already exists
    import shutil, os
    if export and os.path.exists(output_dir):
        shutil.rmtree(output_dir)

    #Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    compiler = pvc.ColorInkjetCompiler(root, voxel_size, output_dir, prefix)

    def print_progress(progress):
        print(f"Compilation progress: {progress*100:.2f}%")

    compiler.set_progress_callback(print_progress)
    compiler.compile()
