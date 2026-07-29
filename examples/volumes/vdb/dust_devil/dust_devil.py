import pyvcad as pv
import pyvcad_medical as med
import pyvcad_compilers as pvc
import pyvcad_rendering as viz

render = True
export = False
use_cylinder = False
cylinder_radius_padding = 10.0
voxel_size = pv.Vec3(0.0423,0.0846,0.027)
scale = 0.18
max_transparency = 1.0

path = "dust_devil.vdb"
prefix = "dust_devil"
output_dir = f"output/dust_devil_scale_{round(scale*100)}_trans_{round(max_transparency*100)}/"

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
if use_cylinder:
    radius = max((volume_bbox_max.x - volume_bbox_min.x), (volume_bbox_max.y - volume_bbox_min.y)) * 0.5
    radius += cylinder_radius_padding / scale
    height = volume_bbox_max.z - volume_bbox_min.z
    object = pv.Cylinder(volume_center, radius, height)
else:
    object = pv.RectPrism.FromMinAndMax(volume_bbox_min, volume_bbox_max)

# Set attributes
object.set_attribute(pv.DefaultAttributes.DENSITY, density_attribute)

# Format: [[density_min, density_max], color (Vec4)]
# This VDB tops out at density ~= 1.0, so the transfer function is tuned to
# put most of the visual range into the lower/mid densities where the wispy
# funnel detail lives. Peak alpha stays below fully opaque so daylight can
# still read the interior twist and self-shadowing in the print.
density_color_map = [
    # Air / noise floor
    [[0.000, 0.010],  pv.Vec4(0.88, 0.83, 0.71, 0.00 * max_transparency)],

    # Thin outer dust veil
    [[0.010, 0.040],  pv.Vec4(0.82, 0.75, 0.60, 0.02 * max_transparency)],
    [[0.040, 0.080],  pv.Vec4(0.77, 0.69, 0.53, 0.05 * max_transparency)],
    [[0.080, 0.140],  pv.Vec4(0.72, 0.63, 0.47, 0.10 * max_transparency)],

    # Main sandy body
    [[0.140, 0.220],  pv.Vec4(0.67, 0.57, 0.40, 0.17 * max_transparency)],
    [[0.220, 0.320],  pv.Vec4(0.61, 0.50, 0.34, 0.27 * max_transparency)],
    [[0.320, 0.440],  pv.Vec4(0.55, 0.44, 0.28, 0.39 * max_transparency)],
    [[0.440, 0.580],  pv.Vec4(0.49, 0.38, 0.23, 0.53 * max_transparency)],

    # Dense ropes and lower funnel core
    [[0.580, 0.720],  pv.Vec4(0.43, 0.33, 0.19, 0.67 * max_transparency)],
    [[0.720, 0.840],  pv.Vec4(0.37, 0.28, 0.16, 0.79 * max_transparency)],
    [[0.840, 0.940],  pv.Vec4(0.31, 0.23, 0.13, 0.88 * max_transparency)],
    [[0.940, 1.001],  pv.Vec4(0.26, 0.19, 0.10, 0.94 * max_transparency)],
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
root = pv.Scale(scale, root)

final_bbox_min, final_bbox_max = root.bounding_box()
print(f"Final BBox Model Size (mm): {final_bbox_max.x - final_bbox_min.x:.2f} x {final_bbox_max.y - final_bbox_min.y:.2f} x {final_bbox_max.z - final_bbox_min.z:.2f}")

if render:
    viz.Render(root)

if export:
    rotated_root = pv.Rotate(0,-90,0, root)
    print(f"Output Directory: {output_dir}")
    # Delete the output directory if it already exists
    import shutil, os
    if export and os.path.exists(output_dir):
        shutil.rmtree(output_dir)

    #Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    compiler = pvc.ColorInkjetCompiler(rotated_root, voxel_size, output_dir, prefix)

    def print_progress(progress):
        print(f"Compilation progress: {progress*100:.2f}%")

    compiler.set_progress_callback(print_progress)
    compiler.compile()
