import pyvcad as pv
import pyvcad_medical as med
import pyvcad_compilers as pvc
import pyvcad_rendering as viz

use_mesh = False
render = True
export = False
voxel_size = pv.Vec3(0.0423,0.0846,0.027)
scale = 0.17
path = "dicom"
mesh_path = "mesh.stl"
prefix = "chest_"
output_dir = f"output/chest_{round(scale*100)}/"
hu_color_map = [
    [[-4000,-100],      pv.Vec4(0,0,0,0.0)],
    [[-100,0],    pv.Vec4(1,1,1,0.01)],
    [[0,25],    pv.Vec4(0/255,34/255,77/255,0.05)],
    [[25,50],    pv.Vec4(67/255,85/255,130/255,0.05)],
    [[50,75],    pv.Vec4(128/255,129/255,145/255,0.05)],
    [[75,100],    pv.Vec4(190/255,172/255,129/255,0.05)],
    [[100,4000],  pv.Vec4(1,0,0,1)],
]

# Load DICOM series
dicom_loader = pv.DICOMLoader(path)
med.imaging.print_loaded_dicom_info(dicom_loader)

# Convert to volume and attribute
dicom_volume = dicom_loader.as_volume()
dicom_attribute = pv.FloatAttribute(dicom_volume)

# Build object
if use_mesh:
    object = pv.Mesh(mesh_path)
else:
    volume_bbox_min, volume_bbox_max = dicom_volume.bounding_box()
    object = pv.RectPrism.FromMinAndMax(volume_bbox_min, volume_bbox_max)
object.set_attribute(pv.DefaultAttributes.HU, dicom_attribute)

hu_entries = [
    pv.LookupTableEntry(kv[0][0], kv[0][1], kv[1]) for kv in hu_color_map
]

# Map HU to color
mod = pv.LookupTableConverter([pv.DefaultAttributes.HU], [pv.DefaultAttributes.COLOR_RGBA], hu_entries, pv.InterpolationMode.STEP)
attr_mod = pv.AttributeModifier(mod, object)

# Rotate and scale
scale = pv.Scale(scale, attr_mod)
root = scale
root = pv.Rotate(0,0,180, root)


final_bbox_min, final_bbox_max = root.bounding_box()
print(f"Final BBox Model Size (mm): {final_bbox_max.x - final_bbox_min.x:.2f} x {final_bbox_max.y - final_bbox_min.y:.2f} x {final_bbox_max.z - final_bbox_min.z:.2f}")

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
