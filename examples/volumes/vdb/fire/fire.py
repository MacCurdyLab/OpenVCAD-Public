import pyvcad as pv
import pyvcad_medical as med
import pyvcad_compilers as pvc
import pyvcad_rendering as viz

render = True
export = False
animate = False
use_cylinder = False
cylinder_radius_padding = 7.0
voxel_size = pv.Vec3(0.0423,0.0846,0.027)
scale = 1.12
max_transparency = 0.8

path = "fire.vdb"
prefix = "fire_"
output_dir = f"output/fire_scale_{round(scale*100)}_trans_{round(max_transparency*100)}/"

# Load VDB volumes
density_volume = pv.vdb_loader.load_float_volume(path, "density")
density_attribute = pv.FloatAttribute(density_volume)

temperature_volume = pv.vdb_loader.load_float_volume(path, "temperature")
temperature_attribute = pv.FloatAttribute(temperature_volume)

# Build object
volume_bbox_min, volume_bbox_max = temperature_volume.bounding_box()
if use_cylinder:
    center = pv.Vec3((volume_bbox_min.x + volume_bbox_max.x) * 0.5,
                     (volume_bbox_min.y + volume_bbox_max.y) * 0.5,
                     (volume_bbox_min.z + volume_bbox_max.z) * 0.5)

    radius = max((volume_bbox_max.z - volume_bbox_min.z), (volume_bbox_max.x - volume_bbox_min.x)) * 0.5
    radius += cylinder_radius_padding / scale
    height = volume_bbox_max.y - volume_bbox_min.y
    object = pv.Cylinder(center, radius, height)
    object = pv.Rotate(90,0,0, object) # Rotate to align volume
    object = pv.BBoxUnion([object])
else:
    object = pv.RectPrism.FromMinAndMax(volume_bbox_min, volume_bbox_max)

# Set attributes
object.set_attribute(pv.DefaultAttributes.DENSITY, density_attribute)
object.set_attribute(pv.DefaultAttributes.TEMPERATURE, temperature_attribute)

def expand_fire_gradient(base_map, num_steps):
    keyframes = []

    for row in base_map:
        temp_start = row[0][0]
        color = row[1]
        d_min = row[2][0]
        d_max = row[2][1]
        trans = row[3]

        keyframes.append({
            'time': temp_start,
            'color': color,
            'd_min': d_min,
            'd_max': d_max,
            'trans': trans
        })

    # Add the final closing keyframe (using the max temp of the last entry)
    last_row = base_map[-1]
    keyframes.append({
        'time': last_row[0][1],
        'color': last_row[1], # Hold the last color
        'd_min': last_row[2][0],
        'd_max': last_row[2][1],
        'trans': last_row[3]
    })

    # 2. Helper function for Linear Interpolation
    def lerp(a, b, t):
        return a + (b - a) * t

    def lerp_vec3(v1, v2, t):
        # Assumes pv.Vec3(x, y, z) constructor and .x, .y, .z access
        return pv.Vec3(
            lerp(v1.x, v2.x, t),
            lerp(v1.y, v2.y, t),
            lerp(v1.z, v2.z, t)
        )

    # 3. Generate the new N steps
    new_map = []

    # Determine the full domain of the gradient
    global_min = keyframes[0]['time']
    global_max = keyframes[-1]['time']
    total_span = global_max - global_min
    step_size = total_span / num_steps

    for i in range(num_steps):
        # Calculate the temperature range for this specific step
        step_t_start = global_min + (i * step_size)
        step_t_end = global_min + ((i + 1) * step_size)

        # We sample the gradient at the center of this new step
        mid_t = (step_t_start + step_t_end) / 2.0

        # Find the two keyframes that bound this mid_t
        start_k = keyframes[0]
        end_k = keyframes[-1]

        for k_idx in range(len(keyframes) - 1):
            if keyframes[k_idx]['time'] <= mid_t <= keyframes[k_idx+1]['time']:
                start_k = keyframes[k_idx]
                end_k = keyframes[k_idx+1]
                break

        # Calculate interpolation factor (0.0 to 1.0) between these two keyframes
        # Avoid division by zero if keyframes are identical
        range_span = end_k['time'] - start_k['time']
        if range_span <= 0:
            local_t = 0.0
        else:
            local_t = (mid_t - start_k['time']) / range_span

        # Interpolate values
        interp_color = lerp_vec3(start_k['color'], end_k['color'], local_t)
        interp_d_min = lerp(start_k['d_min'], end_k['d_min'], local_t)
        interp_d_max = lerp(start_k['d_max'], end_k['d_max'], local_t)
        interp_trans = lerp(start_k['trans'], end_k['trans'], local_t)

        # Append to new map in exact original format
        new_map.append([
            [step_t_start, step_t_end], # [temp_min, temp_max]
            interp_color,               # color (Vec3)
            [interp_d_min, interp_d_max], # [density_min, density_max]
            interp_trans                # transparency
        ])

    return new_map

# Format: [[temp_min, temp_max], color (Vec3), [density_min, density_max], transparency] forms each range
temp_density_color_map = [
    [[0,1],      pv.Vec3(1,1,1),         [0,0.01],    0.00*max_transparency],    # Transparent for open air
    [[1,7.5],    pv.Vec3(.1,.1,.1),      [0.01,0.1],  0.15*max_transparency],    # Dark gray for low temp smoke
    [[7.5,15],   pv.Vec3(0.5,0,0),       [0.1,0.2],   0.30*max_transparency],    # Dark red for embers
    [[15,22.5],  pv.Vec3(0.9,0.2,0.05),  [0.2,0.5],   0.55*max_transparency],    # Vivid red for flame
    [[22.5,30],  pv.Vec3(1.0,0.6,0.05),  [0.5,0.75],  0.80*max_transparency],    # Orange for hotter flame
    [[30,37.5],  pv.Vec3(1.0,0.9,0.2),   [0.75,1.36], 0.95*max_transparency],    # Yellow for even hotter flame
    [[37.5,46],  pv.Vec3(1.0,1.0,1.0),   [0.75,1.36], 1.0*max_transparency],     # White for hottest flame
]

new_map = expand_fire_gradient(temp_density_color_map, 96)

# Multi-input independent STEP: temperature -> RGB (Vec3), density -> alpha (double),
# assembled into a single color_rgba (Vec4) output.
entries = [
    pv.LookupTableEntry(
        [(row[0][0], row[0][1]), (row[2][0], row[2][1])],
        [row[1], row[3]]
    )
    for row in new_map
]

mod = pv.LookupTableConverter(
    [pv.DefaultAttributes.TEMPERATURE, pv.DefaultAttributes.DENSITY],
    [pv.DefaultAttributes.COLOR_RGBA],
    entries,
    pv.InterpolationMode.STEP
)
root = pv.AttributeModifier(mod, object)
root = pv.Scale(scale, root)

root = pv.Rotate(-90,0,0, root) # Stand up along the z-axis

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


if animate:
    from pyvcad_rendering import Render_Sweep_Animation, Render_Turntable_Animation

    sweep_out_dir = "sweep_animation"
    turntable_out_dir = "turntable_animation"
    
    # Custom settings to make it look nice
    settings = {
        "quality": "high",
        "render_mode": "volumetric",
        "visualized_attribute": "color_rgba",         # Replace "none" with attribute name if available
        "show_bbox": False,
        "show_origin": False,
        "background_color": (1.0, 1.0, 1.0),          # White background
        "transparent_background": True                # Set True for transparent output
    }
    
    # Render a 3-second GIF at 30fps (auto-calculates 90 frames)
    # The normal sweeps along the X axis by default if axis="x"
    # Over a 3 second duration
    Render_Sweep_Animation(
        vcad_object=root, 
        materials=pv.default_materials, 
        output_dir=sweep_out_dir, 
        axis="z",                    # Axis to sweep along ("x", "y", "z")
        duration=5.0,                # Total animation length in seconds for one pass
        fps=10,                      # Frames per second (default)
        loop=True,                   # Loop back forth (forward then back to start)
        pause_seconds=0,             # Pause at the beginning and end
        settings=settings,
        output_format="all",         # Options: "gif", "mp4", "webm", "all"
        keep_frames=False            # Set True to keep the intermediate PNG files
    ) 

    Render_Turntable_Animation(
        vcad_object=root, 
        materials=pv.default_materials, 
        output_dir=turntable_out_dir, 
        duration=5.0,                # Total animation length in seconds
        fps=20,                      # Frames per second (default)
        distance_multiplier=2.0, 
        elevation_angle_deg=25.0, 
        settings=settings,
        output_format="all",         # Options: "gif", "mp4", "webm", "all"
        keep_frames=False            # Set True to keep the intermediate PNG files
    )
