import os

import pyvcad as pv
import pyvcad_medical as med
import pyvcad_compilers as pvc
import pyvcad_rendering as viz

render = True
export = False
voxel_size = pv.Vec3(0.0423, 0.0846, 0.027)
# scale = 0.1
scale = 0.065
max_transparency = 0.9

frame_numbers = [5, 25, 35, 55, 65, 85, 105]
# frame_numbers = [5, 15, 25, 35, 45, 55, 65, 75, 85, 95, 105, 115]
sequence_dir = "sequence"
sequence_file_template = "explosion_{n}.vdb"

printer_bed_size_x = 480.0
printer_bed_size_y = 380.0
sample_spacing = 0

prefix = "explosion_"
output_dir = (
    f"output/explosion_seq_{len(frame_numbers)}frames_"
    f"scale_{round(scale * 100)}_trans_{round(max_transparency * 100)}/"
)

# Build a true 2D temperature x density -> COLOR_RGBA lookup so low-density
# background regions interpolate to transparent instead of remaining undefined.
def lerp(a, b, t):
    return a + (b - a) * t

def lerp_vec3(v1, v2, t):
    return pv.Vec3(
        lerp(v1.x, v2.x, t),
        lerp(v1.y, v2.y, t),
        lerp(v1.z, v2.z, t)
    )

def sample_scalar_ramp(ramp, value):
    if value <= ramp[0][0]:
        return ramp[0][1]

    for i in range(len(ramp) - 1):
        x0, y0 = ramp[i]
        x1, y1 = ramp[i + 1]
        if value <= x1:
            if x1 <= x0:
                return y1
            return lerp(y0, y1, (value - x0) / (x1 - x0))

    return ramp[-1][1]

def sample_color_ramp(ramp, value):
    if value <= ramp[0][0]:
        return ramp[0][1]

    for i in range(len(ramp) - 1):
        x0, c0 = ramp[i]
        x1, c1 = ramp[i + 1]
        if value <= x1:
            if x1 <= x0:
                return c1
            return lerp_vec3(c0, c1, (value - x0) / (x1 - x0))

    return ramp[-1][1]

def build_rgba_grid_entries(temp_points, density_points, color_ramp, density_alpha_ramp, temp_gate_ramp):
    entries = []

    for density in density_points:
        density_alpha = sample_scalar_ramp(density_alpha_ramp, density)
        for temperature in temp_points:
            color = sample_color_ramp(color_ramp, temperature)
            temp_gate = sample_scalar_ramp(temp_gate_ramp, temperature)
            alpha = density_alpha * temp_gate * max_transparency
            rgba = pv.Vec4(color.x, color.y, color.z, alpha)
            entries.append(pv.LookupTableEntry([temperature, density], rgba))

    return entries

temp_points = [0.0, 60.0, 250.0, 600.0, 1000.0, 1400.0, 1900.0, 2500.0, 3100.0, 3600.0, 3900.0]
density_points = [0.0, 0.01, 0.04, 0.09, 0.16, 0.25, 0.35, 0.46, 0.54, 0.60]

temp_color_ramp = [
    (0.0,    pv.Vec3(0.05, 0.05, 0.05)),
    (60.0,   pv.Vec3(0.06, 0.06, 0.06)),
    (250.0,  pv.Vec3(0.09, 0.09, 0.09)),
    (600.0,  pv.Vec3(0.16, 0.14, 0.12)),
    (1000.0, pv.Vec3(0.24, 0.19, 0.14)),
    (1400.0, pv.Vec3(0.55, 0.14, 0.03)),
    (1900.0, pv.Vec3(0.95, 0.30, 0.03)),
    (2500.0, pv.Vec3(1.00, 0.62, 0.03)),
    (3100.0, pv.Vec3(1.00, 0.88, 0.14)),
    (3600.0, pv.Vec3(1.00, 0.98, 0.78)),
    (3900.0, pv.Vec3(1.00, 1.00, 0.98)),
]

density_alpha_ramp = [
    (0.0, 0.00),
    (0.01, 0.00),
    (0.04, 0.08),
    (0.09, 0.16),
    (0.16, 0.27),
    (0.25, 0.40),
    (0.35, 0.54),
    (0.46, 0.68),
    (0.54, 0.82),
    (0.60, 0.92),
]

temp_gate_ramp = [
    (0.0, 0.00),
    (60.0, 1.00),
    (3900.0, 1.00),
]

entries = build_rgba_grid_entries(
    temp_points,
    density_points,
    temp_color_ramp,
    density_alpha_ramp,
    temp_gate_ramp
)

mod = pv.LookupTableConverter(
    [pv.DefaultAttributes.TEMPERATURE, pv.DefaultAttributes.DENSITY],
    [pv.DefaultAttributes.COLOR_RGBA],
    entries,
    pv.InterpolationMode.LINEAR
)


def load_frame_data(frame_number):
    path = os.path.join(sequence_dir, sequence_file_template.format(n=frame_number))
    if not os.path.isfile(path):
        raise FileNotFoundError(
            f"Missing frame {frame_number}: expected file '{path}'."
        )

    density_volume = pv.vdb_loader.load_float_volume(path, "density")
    density_attribute = pv.FloatAttribute(density_volume)

    temperature_volume = pv.vdb_loader.load_float_volume(path, "temperature")
    temperature_attribute = pv.FloatAttribute(temperature_volume)
    volume_bbox_min, volume_bbox_max = temperature_volume.bounding_box()
    return {
        "frame_number": frame_number,
        "density_attribute": density_attribute,
        "temperature_attribute": temperature_attribute,
        "bbox_min": volume_bbox_min,
        "bbox_max": volume_bbox_max,
    }


def build_frame(frame_data, converter, canonical_bbox_min, canonical_bbox_max):
    frame_object = pv.RectPrism.FromMinAndMax(canonical_bbox_min, canonical_bbox_max)
    frame_object.set_attribute(
        pv.DefaultAttributes.DENSITY,
        frame_data["density_attribute"],
    )
    frame_object.set_attribute(
        pv.DefaultAttributes.TEMPERATURE,
        frame_data["temperature_attribute"],
    )

    root = pv.AttributeModifier(converter, frame_object)
    root = pv.Scale(scale, root)
    root = pv.Rotate(90, 0, 0, root)
    return root


if not frame_numbers:
    raise ValueError("frame_numbers must contain at least one frame index.")

frame_data = [load_frame_data(frame_number) for frame_number in frame_numbers]

canonical_bbox_min = frame_data[0]["bbox_min"]
canonical_bbox_max = frame_data[0]["bbox_max"]
for data in frame_data[1:]:
    bbox_min = data["bbox_min"]
    bbox_max = data["bbox_max"]
    canonical_bbox_min = pv.Vec3(
        min(canonical_bbox_min.x, bbox_min.x),
        min(canonical_bbox_min.y, bbox_min.y),
        min(canonical_bbox_min.z, bbox_min.z),
    )
    canonical_bbox_max = pv.Vec3(
        max(canonical_bbox_max.x, bbox_max.x),
        max(canonical_bbox_max.y, bbox_max.y),
        max(canonical_bbox_max.z, bbox_max.z),
    )

frames = [
    build_frame(data, mod, canonical_bbox_min, canonical_bbox_max)
    for data in frame_data
]

frame_bboxes = []
max_width = 0.0
max_depth = 0.0
for frame in frames:
    frame_bbox_min, frame_bbox_max = frame.bounding_box()
    frame_bboxes.append((frame_bbox_min, frame_bbox_max))
    width = frame_bbox_max.x - frame_bbox_min.x
    depth = frame_bbox_max.y - frame_bbox_min.y
    if width > max_width:
        max_width = width
    if depth > max_depth:
        max_depth = depth

pitch_x = max_width + sample_spacing
pitch_y = max_depth + sample_spacing

if pitch_x <= 0.0 or pitch_y <= 0.0:
    raise ValueError("Computed frame pitch must be positive.")

max_columns = int((printer_bed_size_x + sample_spacing) // pitch_x)
max_rows = int((printer_bed_size_y + sample_spacing) // pitch_y)
capacity = max_columns * max_rows

if capacity <= 0:
    raise ValueError(
        "The configured build plate is too small for one frame. "
        f"Frame footprint with spacing is {pitch_x:.3f} x {pitch_y:.3f} mm, "
        f"bed size is {printer_bed_size_x:.3f} x {printer_bed_size_y:.3f} mm."
    )

if len(frames) > capacity:
    raise ValueError(
        f"Requested {len(frames)} frames but the configured build plate fits at most {capacity}."
    )

bbox_union = pv.BBoxUnion()
for frame_index, frame in enumerate(frames):
    col = frame_index % max_columns
    row = frame_index // max_columns
    frame_bbox_min, _ = frame_bboxes[frame_index]
    tx = col * pitch_x - frame_bbox_min.x
    ty = row * pitch_y - frame_bbox_min.y
    tz = -frame_bbox_min.z
    bbox_union.add_child(pv.Translate(tx, ty, tz, frame))

root = bbox_union

final_bbox_min, final_bbox_max = root.bounding_box()
print(f"Final BBox Model Size (mm): {final_bbox_max.x - final_bbox_min.x:.2f} x {final_bbox_max.y - final_bbox_min.y:.2f} x {final_bbox_max.z - final_bbox_min.z:.2f}")

if render:
    viz.Render(root)

if export:
    print(f"Output Directory: {output_dir}")
    # Delete the output directory if it already exists
    import shutil
    if export and os.path.exists(output_dir):
        shutil.rmtree(output_dir)

    #Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    compiler = pvc.ColorInkjetCompiler(root, voxel_size, output_dir, prefix)

    def print_progress(progress):
        print(f"Compilation progress: {progress*100:.2f}%")

    compiler.set_progress_callback(print_progress)
    compiler.compile()
