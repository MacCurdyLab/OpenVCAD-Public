import pyvcad as pv
import pyvcad_medical as med
import pyvcad_compilers as pvc
import pyvcad_rendering as viz

# Configuration
render = True
export = False
voxel_size = pv.Vec3(0.0423,0.0846,0.027)
scale = 0.3135
prefix = "apple_vision_pro_"
path = "dicom"
mesh_path = "mesh.stl"
output_dir = f"output/apple_vision_pro_{round(scale*100)}/"

# Build HU color map with sigmoid opacity
opacity_function = lambda t: med.color_maps.sigmoid_opacity_base(t, k=9.0, x0=0.2)
hu_color_map=med.color_maps.create_linear_gradient_hu_map(110, 255, palette=med.color_maps.get_color_palette("jet"), steps=30, opacity_function=opacity_function)

# Load DICOM series
dicom_loader = pv.DICOMLoader(path)
med.imaging.print_loaded_dicom_info(dicom_loader)

# Convert to volume and attribute
dicom_volume = dicom_loader.as_volume()
dicom_attribute = pv.FloatAttribute(dicom_volume)

object = pv.Mesh(mesh_path,disable_validation=True,compensate_slicer_ras=False)
object.set_attribute(pv.DefaultAttributes.HU, dicom_attribute)

mod = pv.LookupTableConverter([pv.DefaultAttributes.HU], [pv.DefaultAttributes.COLOR_RGBA], hu_color_map, pv.InterpolationMode.STEP)
object = pv.AttributeModifier(mod, object)

object = pv.Scale(scale, object)
object = pv.Rotate(0,0,37, object)
object = pv.Rotate(90,0,0, object)

# Print final bounding box size (after scaling)
final_bbox_min, final_bbox_max = object.bounding_box()
print(f"Final Model BBox Size (mm): {final_bbox_max.x - final_bbox_min.x:.2f} x {final_bbox_max.y - final_bbox_min.y:.2f} x {final_bbox_max.z - final_bbox_min.z:.2f}")

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
