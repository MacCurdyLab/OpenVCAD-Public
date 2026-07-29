import pyvcad as pv
import pyvcad_medical as med
import pyvcad_compilers as pvc
import pyvcad_rendering as viz

use_mesh = False
render = True
export = False
voxel_size = pv.Vec3(0.0423,0.0846,0.027)
scale = 1.25
max_transparency = 1.0
palette = "a"

path = "bunny_cloud.vdb"
prefix = "bunny_cloud"
output_dir = f"output/bunny_palette_{palette}_scale_{round(scale*100)}_trans_{round(max_transparency*100)}_mesh_{use_mesh}/"

# Load VDB volumes
density_volume = pv.vdb_loader.load_float_volume(path, "density", center=True)
density_attribute = pv.FloatAttribute(density_volume)

volume_bbox_min, volume_bbox_max = density_volume.bounding_box()
volume_center = pv.Vec3(
    (volume_bbox_min.x + volume_bbox_max.x) * 0.5,
    (volume_bbox_min.y + volume_bbox_max.y) * 0.5,
    (volume_bbox_min.z + volume_bbox_max.z) * 0.5,
)
print(f"Volume's Center (mm): {volume_center.x:.2f}, {volume_center.y:.2f}, {volume_center.z:.2f}")

# Build object
if use_mesh:
    object = pv.Mesh("mesh.stl", disable_validation=True, center=True)
    object = pv.Rotate(90,0,0, object)
    object_bbox_min, object_bbox_max = object.bounding_box()
    scale = (volume_bbox_max.z - volume_bbox_min.z) / (object_bbox_max.z - object_bbox_min.z)
    scale = scale * 1.1
    print(f"Mesh Scale Factor: {scale:.4f}")
    object = pv.Scale(scale, object)
    object_bbox_min, object_bbox_max = object.bounding_box()
    object_center = pv.Vec3(
        (object_bbox_min.x + object_bbox_max.x) * 0.5,
        (object_bbox_min.y + object_bbox_max.y) * 0.5,
        (object_bbox_min.z + object_bbox_max.z) * 0.5,
    )
    object = pv.Translate(
        volume_center.x - object_center.x,
        volume_center.y - object_center.y,
        volume_center.z - object_center.z,
        object
    )
else:
    object = pv.RectPrism.FromMinAndMax(volume_bbox_min, volume_bbox_max)

# Set attributes
object.set_attribute(pv.DefaultAttributes.DENSITY, density_attribute)

# Format: [[density_min, density_max], color (Vec4)]
if palette == "a":
    density_color_map = [
        [[0,0.01],      pv.Vec4(1,1,1, 0.00*max_transparency)],
        [[0.01,0.435],    pv.Vec4(1,1,1, 0.10*max_transparency)],
        [[0.435,1.305],   pv.Vec4(1,1,1, 0.25*max_transparency)],
        [[1.305,1.74],  pv.Vec4(1,1,1, 0.50*max_transparency)],
        [[1.74,2.175],  pv.Vec4(1,1,1, 0.75*max_transparency)],
        [[2.175,2.61],  pv.Vec4(1,1,1, 1.0*max_transparency)],
    ]
else:
    density_color_map = [
        # Noise floor / very low density
        [[0.000, 0.010],  pv.Vec4(1, 1, 1, 0.00 * max_transparency)],

        # Gradual ramp up
        [[0.010, 0.217],  pv.Vec4(1, 1, 1, 0.05 * max_transparency)],
        [[0.217, 0.435],  pv.Vec4(1, 1, 1, 0.10 * max_transparency)],
        [[0.435, 0.652],  pv.Vec4(1, 1, 1, 0.18 * max_transparency)],
        [[0.652, 0.870],  pv.Vec4(1, 1, 1, 0.28 * max_transparency)],
        [[0.870, 1.087],  pv.Vec4(1, 1, 1, 0.40 * max_transparency)],
        [[1.087, 1.305],  pv.Vec4(1, 1, 1, 0.52 * max_transparency)],

        # Higher density core
        [[1.305, 1.522],  pv.Vec4(1, 1, 1, 0.65 * max_transparency)],
        [[1.522, 1.740],  pv.Vec4(1, 1, 1, 0.76 * max_transparency)],
        [[1.740, 1.957],  pv.Vec4(1, 1, 1, 0.85 * max_transparency)],
        [[1.957, 2.175],  pv.Vec4(1, 1, 1, 0.92 * max_transparency)],
        [[2.175, 3],  pv.Vec4(1, 1, 1, 1.00 * max_transparency)],
    ]

entries = [
    pv.LookupTableEntry(row[0][0], row[0][1], row[1])
    for row in density_color_map
]
mod = pv.LookupTableConverter(
    [pv.DefaultAttributes.DENSITY],
    [pv.DefaultAttributes.COLOR_RGBA],
    entries,
    pv.InterpolationMode.STEP
)
root = pv.AttributeModifier(mod, object)

root = pv.Rotate(-90,0,0, root)
root = pv.Scale(scale, root)

final_bbox_min, final_bbox_max = root.bounding_box()
print(f"Final BBox Model Size (mm): {final_bbox_max.x - final_bbox_min.x:.2f} x {final_bbox_max.y - final_bbox_min.y:.2f} x {final_bbox_max.z - final_bbox_min.z:.2f}")

if render:
    viz.Render(root)

if export:
    root = pv.Rotate(90,0,0, root) # Rotate back to original orientation for printing

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
