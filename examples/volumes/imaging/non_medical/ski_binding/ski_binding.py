import pyvcad as pv
import pyvcad_medical as med
import pyvcad_compilers as pvc
import pyvcad_rendering as viz

use_mesh = True
render = True
export = False
voxel_size = pv.Vec3(0.0423,0.0846,0.027)
scale = 0.3
prefix = "ski_binding_"
path = "dicom"
mesh_path = "ski_binding.stl"
output_dir = f"output/ski_binding_{round(scale*100)}/"

# Build HU color map with re-mapped sigmoid opacity
opacity_function = lambda t: med.color_maps.re_range_opacity(t, lambda t: med.color_maps.sigmoid_opacity_base(t, k=20.0, x0=0.9), lower_opacity=0.01, upper_opacity=0.05)
hu_color_map_filler=med.color_maps.create_linear_gradient_hu_map(25, 125, palette=med.color_maps.get_color_palette("jet"), steps=30, opacity_function=opacity_function)

# Add solid color for high HU values
hu_color_map_solid=[
    pv.LookupTableEntry(125, 255, pv.Vec4(1,1,0, 1.0)),
]
hu_color_map = hu_color_map_filler + hu_color_map_solid

# Load DICOM series and print info
dicom_loader = pv.DICOMLoader(path, center=True)
med.imaging.print_loaded_dicom_info(dicom_loader)

# Convert to volume and attribute
dicom_volume = dicom_loader.as_volume()
dicom_attribute = pv.FloatAttribute(dicom_volume)

# Build object
if use_mesh:
    object = pv.Mesh(mesh_path,center=True,disable_validation=True)
else:
    volume_bbox_min, volume_bbox_max = dicom_volume.bounding_box()
    object = pv.RectPrism.FromMinAndMax(volume_bbox_min, volume_bbox_max)
object.set_attribute(pv.DefaultAttributes.HU, dicom_attribute)

# Apply HU to color conversion
mod = pv.LookupTableConverter([pv.DefaultAttributes.HU], [pv.DefaultAttributes.COLOR_RGBA], hu_color_map, pv.InterpolationMode.STEP)
attr_mod = pv.AttributeModifier(mod, object)

# Rotate and scale
root = pv.Scale(scale, attr_mod)
root = pv.Rotate(0,0,90, root)
root = pv.Rotate(0,118,0, root)

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
