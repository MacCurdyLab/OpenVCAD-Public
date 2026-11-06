"""
OpenVCAD logo cloud: a cumulus cloud shaped like the logo V, floating in a clear resin block.

The cloud is procedural (see generate_logo_cloud.py, which builds it in numpy + scipy and loads it
with pv.FloatVolume.from_array). Running this example only needs pyvcad and the shipped VDBs. It is cached as two single-grid VDB files, plus a second pair with the
word "OpenVCAD" in cloud lettering under the V (``with_text``):

- ``light`` (0..1) is the sunlight baked into the cloud: Beer-Lambert shadowing toward a sun at
  the upper front left plus sky light and ambient occlusion. It picks the colour, from a cool
  blue-grey in the shadowed creases and underside to a warm white on the sunlit billows.
- ``density`` (0..1) picks how opaque each voxel is; ``max_transparency`` scales it. Wispy
  fringes stay faint and the dense core turns solid white.

Printed resin doesn't scatter light like a real cloud, so baking the lighting into the colour is
what makes the print read as a sunlit cumulus under ordinary room light. The grids are Y up with
the logo facing +Z; the block is stood up along Z like the fire examples.

``add_text`` extends the block below the cloud and floats solid "OpenVCAD" lettering there, for
prints that should carry a plain-text label rather than (or as well as) the cloud lettering.
"""
import os
import shutil

import numpy as np
import pyvcad as pv
import pyvcad_compilers as pvc
import pyvcad_rendering as viz

render = True
export = False
with_text = False           # True loads the variant with "OpenVCAD" in cloud lettering under the V
add_text = False            # True extends the block below the cloud and floats solid "OpenVCAD" lettering in it
voxel_size = pv.Vec3(0.0423, 0.0846, 0.027)
scale = 1.0
max_transparency = 0.85
clear_margin = 6.0          # mm of clear resin between the cloud and every face of the block
text_height = 11.0          # font size of the solid lettering (grid units, scaled with the cloud)
text_depth = 3.0            # lettering thickness along the viewing axis
text_gap = 3.0              # clear resin between the bottom of the cloud and the lettering
text_color = (0.24, 0.28, 0.40)  # the cloud's shadow tone

name = "logo_cloud_text" if with_text else "logo_cloud"
if add_text:
    name += "_label"
prefix = f"{name}_"
output_dir = f"output/{name}_scale_{round(scale*100)}_trans_{round(max_transparency*100)}/"

# Load both grids; they share a transform, so they line up voxel for voxel
grid_name = "logo_cloud_text" if with_text else "logo_cloud"
density_volume = pv.vdb_loader.load_float_volume(f"{grid_name}_density.vdb", "density")
light_volume = pv.vdb_loader.load_float_volume(f"{grid_name}_light.vdb", "light")


def visible_bounds(volume, threshold, step=0.5):
    """Bounds of the region where the grid reaches `threshold`, sampled every `step` and padded by one step.
    The grid's own bounding box carries a lot of empty air around the cloud."""
    grid_min, grid_max = volume.bounding_box()
    probe = pv.RectPrism.FromMinAndMax(grid_min, grid_max)
    probe.set_attribute(pv.DefaultAttributes.DENSITY, pv.FloatAttribute(volume))
    axes = [np.arange(lo, hi, step) for lo, hi in ((grid_min.x, grid_max.x), (grid_min.y, grid_max.y), (grid_min.z, grid_max.z))]
    points = np.stack(np.meshgrid(*axes, indexing="ij"), -1).reshape(-1, 3).astype(np.float32)
    sampler = pv.TreeSampler(probe, pv.Vec3(step, step, step))
    sampler.set_undefined_attribute_pattern_enabled(False)
    values = np.asarray(sampler.sample_points_to_float_array(points, pv.DefaultAttributes.DENSITY))
    visible = points[values >= threshold]
    lo = np.maximum(visible.min(axis=0) - step, (grid_min.x, grid_min.y, grid_min.z))
    hi = np.minimum(visible.max(axis=0) + step, (grid_max.x, grid_max.y, grid_max.z))
    return pv.Vec3(*lo), pv.Vec3(*hi)


# A clear block around the visible cloud with clear_margin of padding on every side (in final mm).
# Density under 0.02 prints fully clear (see density_alphas), so the block is fitted to that.
cloud_min, cloud_max = visible_bounds(density_volume, 0.02)
pad = clear_margin / scale
block_min_y = cloud_min.y - pad
block_min_x, block_max_x = cloud_min.x - pad, cloud_max.x + pad

# Optional solid lettering under the cloud, facing +Z like the logo, centred in the block's depth
if add_text:
    # Text lays its glyphs out turned 180 degrees in XY; turn them back so they read upright with +Y up
    label = pv.Rotate(0, 0, 180, pv.Text("OpenVCAD", text_height, text_depth, aspect=pv.FontAspect.Bold, font="Arial"))
    label.prepare(voxel_size, 0.5)
    label_min, label_max = label.bounding_box()
    label = pv.Translate((cloud_min.x + cloud_max.x) / 2 - (label_min.x + label_max.x) / 2,
                         cloud_min.y - text_gap - label_max.y,
                         (cloud_min.z + cloud_max.z) / 2, label)
    label.set_attribute(pv.DefaultAttributes.COLOR_RGBA, pv.Vec4Attribute(*[str(c) for c in text_color], "1.0"))
    block_min_y = cloud_min.y - text_gap - (label_max.y - label_min.y) - pad
    half_label = (label_max.x - label_min.x) / 2
    block_min_x = min(block_min_x, (cloud_min.x + cloud_max.x) / 2 - half_label - pad)
    block_max_x = max(block_max_x, (cloud_min.x + cloud_max.x) / 2 + half_label + pad)

block = pv.RectPrism.FromMinAndMax(pv.Vec3(block_min_x, block_min_y, cloud_min.z - pad),
                                   pv.Vec3(block_max_x, cloud_max.y + pad, cloud_max.z + pad))
block.set_attribute(pv.DefaultAttributes.DENSITY, pv.FloatAttribute(density_volume))
block.set_attribute("light", pv.FloatAttribute(light_volume))

# Baked light -> colour: shadowed underside, creases, mid tones, sunlit billows
light_colors = [
    (0.00, (0.24, 0.28, 0.40)),
    (0.20, (0.42, 0.48, 0.60)),
    (0.40, (0.66, 0.71, 0.80)),
    (0.60, (0.88, 0.90, 0.94)),
    (0.80, (1.00, 0.99, 0.96)),
    (1.00, (1.00, 0.95, 0.84)),
]

# Density -> alpha: clear air, faint wisps, then a quick rise into an opaque core
density_alphas = [
    (0.00, 0.00),
    (0.02, 0.00),
    (0.05, 0.04),
    (0.15, 0.12),
    (0.30, 0.30),
    (0.50, 0.55),
    (0.75, 0.82),
    (1.00, 1.00),
]


def interpolate(stops, t):
    """Piecewise-linear lookup in a sorted list of (position, value) stops; value is a float or tuple."""
    for (t0, v0), (t1, v1) in zip(stops, stops[1:]):
        if t <= t1:
            f = (t - t0) / (t1 - t0)
            return tuple(a + (b - a) * f for a, b in zip(v0, v1)) if isinstance(v0, tuple) else v0 + (v1 - v0) * f
    return stops[-1][1]


# Two independent STEP inputs, as in fire.py: light -> RGB and density -> alpha, packed into COLOR_RGBA.
# Each table is resampled into `steps` narrow bins so the steps are invisible.
steps = 96
entries = []
for i in range(steps):
    lo, hi = i / steps, (i + 1) / steps
    if i == steps - 1:
        hi = 2.0                                     # catch anything at or above 1
    color = interpolate(light_colors, (i + 0.5) / steps)
    alpha = interpolate(density_alphas, (i + 0.5) / steps) * max_transparency
    if i == 0:
        alpha, lo = 0.0, -1.0                        # empty voxels sample 0 and must stay clear
    entries.append(pv.LookupTableEntry([(lo, hi), (lo, hi)], [pv.Vec3(*color), alpha]))

converter = pv.LookupTableConverter(["light", pv.DefaultAttributes.DENSITY], [pv.DefaultAttributes.COLOR_RGBA],
                                    entries, pv.InterpolationMode.STEP)
root = pv.AttributeModifier(converter, block)
if add_text:
    root = pv.Union(0.0, [label, root])  # the lettering comes first so its colour wins inside it
root = pv.Scale(scale, root)
root = pv.Rotate(-90, 0, 0, root)  # Stand up along the z-axis

final_bbox_min, final_bbox_max = root.bounding_box()
print(f"Final BBox Model Size (mm): {final_bbox_max.x - final_bbox_min.x:.2f} x {final_bbox_max.y - final_bbox_min.y:.2f} x {final_bbox_max.z - final_bbox_min.z:.2f}")

if render:
    viz.Render(root)

if export:
    print(f"Output Directory: {output_dir}")
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)
    compiler = pvc.ColorInkjetCompiler(pv.Rotate(0, -90, 0, root), voxel_size, output_dir, prefix)
    compiler.set_progress_callback(lambda progress: print(f"Compilation progress: {progress*100:.2f}%"))
    compiler.compile()
