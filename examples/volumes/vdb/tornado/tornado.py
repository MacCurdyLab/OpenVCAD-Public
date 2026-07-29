import pyvcad as pv
import pyvcad_medical as med
import pyvcad_compilers as pvc
import pyvcad_rendering as viz

render = True
export = False
use_cylinder = False
cylinder_radius_padding = 0.0
voxel_size = pv.Vec3(0.0423,0.0846,0.027)
scale = 0.15
max_transparency = 1.0

path = "tornado.vdb"
prefix = "tornado"
output_dir = f"output/tornado_scale_{round(scale*100)}_trans_{round(max_transparency*100)}/"

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
# This VDB tops out at density ~= 0.54. The goal here is a darker tornado
# body than the dust-devil example: warm tan at the wispy perimeter, then a
# quick falloff into smoky brown so the core reads heavy under natural light
# while still leaving enough transmission for interior twist and shadowing.
density_color_map = [
    # Air / noise floor
    [[0.000, 0.008],  pv.Vec4(0.79, 0.68, 0.49, 0.00 * max_transparency)],

    # Thin illuminated wisps
    [[0.008, 0.020],  pv.Vec4(0.75, 0.62, 0.43, 0.02 * max_transparency)],
    [[0.020, 0.040],  pv.Vec4(0.69, 0.56, 0.37, 0.06 * max_transparency)],
    [[0.040, 0.070],  pv.Vec4(0.62, 0.48, 0.30, 0.12 * max_transparency)],

    # Main funnel body
    [[0.070, 0.110],  pv.Vec4(0.55, 0.40, 0.24, 0.21 * max_transparency)],
    [[0.110, 0.160],  pv.Vec4(0.47, 0.32, 0.18, 0.32 * max_transparency)],
    [[0.160, 0.220],  pv.Vec4(0.40, 0.27, 0.15, 0.46 * max_transparency)],
    [[0.220, 0.290],  pv.Vec4(0.33, 0.21, 0.11, 0.61 * max_transparency)],

    # Dense rotating core
    [[0.290, 0.370],  pv.Vec4(0.26, 0.16, 0.09, 0.74 * max_transparency)],
    [[0.370, 0.450],  pv.Vec4(0.19, 0.11, 0.06, 0.85 * max_transparency)],
    [[0.450, 0.510],  pv.Vec4(0.14, 0.08, 0.04, 0.93 * max_transparency)],
    [[0.510, 0.539],  pv.Vec4(0.10, 0.06, 0.03, 0.97 * max_transparency)],
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
    # rotated_root = pv.Rotate(-40,-40,0, root)
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
