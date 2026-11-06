"""
OpenVCAD logo on fire: a full-colour volumetric print of the logo V burning inside a clear block.

logo_fire.vdb is a Blender Mantaflow fire/smoke simulation of the logo (see
generate_logo_fire_blender.py and package_logo_fire_vdb.py). Running this example only needs
pyvcad and the shipped logo_fire.vdb; regenerating the VDB additionally needs Blender 5.x (its
bundled Python provides bpy and openvdb). It carries the same two grids as fire.vdb, so this
example follows fire/fire.py:

- ``temperature`` (0..46) picks the colour: open air and cool smoke white, warm smoke dark grey,
  then embers, red, orange, yellow and white-hot. The logo layers themselves sit at the top of
  that range (front layer white-hot, deeper layers yellow, orange and red) so the V reads as a
  glowing ember with flames rising off it.
- ``density`` (0..1.36) picks how opaque each voxel is; ``max_transparency`` scales it.

The grids are Y-up with the logo facing +Z; the block is stood up along Z like fire.py.
``clear_margin`` pads the block with clear resin on every face.
"""
import os
import shutil

import pyvcad as pv
import pyvcad_compilers as pvc
import pyvcad_rendering as viz

render = True
export = False
animate = False
voxel_size = pv.Vec3(0.0423, 0.0846, 0.027)
scale = 1.0
max_transparency = 0.8
clear_margin = 6.0   # mm of clear resin padding the volume on every face (print units, after scale)

path = "logo_fire.vdb"
prefix = "logo_fire_"
output_dir = f"output/logo_fire_scale_{round(scale*100)}_trans_{round(max_transparency*100)}/"

# Load the VDB grids as attributes
density_volume = pv.vdb_loader.load_float_volume(path, "density")
temperature_volume = pv.vdb_loader.load_float_volume(path, "temperature")

# A clear block around the volume. The grids fade to zero at their faces and read zero outside, so
# the margin prints as clear resin and no smoke or flame touches the block surface.
volume_bbox_min, volume_bbox_max = temperature_volume.bounding_box()
pad = clear_margin / scale
block = pv.RectPrism.FromMinAndMax(pv.Vec3(volume_bbox_min.x - pad, volume_bbox_min.y - pad, volume_bbox_min.z - pad),
                                   pv.Vec3(volume_bbox_max.x + pad, volume_bbox_max.y + pad, volume_bbox_max.z + pad))
block.set_attribute(pv.DefaultAttributes.DENSITY, pv.FloatAttribute(density_volume))
block.set_attribute(pv.DefaultAttributes.TEMPERATURE, pv.FloatAttribute(temperature_volume))


def expand_fire_gradient(base_map, num_steps):
    """Resample a coarse [temp range, colour, density range, transparency] table into num_steps
    evenly spaced, linearly interpolated rows (same format)."""
    keyframes = [{'time': row[0][0], 'color': row[1], 'd_min': row[2][0], 'd_max': row[2][1], 'trans': row[3]}
                 for row in base_map]
    last = base_map[-1]
    keyframes.append({'time': last[0][1], 'color': last[1], 'd_min': last[2][0], 'd_max': last[2][1], 'trans': last[3]})

    def lerp(a, b, t):
        return a + (b - a) * t

    lo, hi = keyframes[0]['time'], keyframes[-1]['time']
    step = (hi - lo) / num_steps
    new_map = []
    for i in range(num_steps):
        t0 = lo + i * step
        mid = t0 + 0.5 * step
        a, b = keyframes[0], keyframes[-1]
        for k in range(len(keyframes) - 1):
            if keyframes[k]['time'] <= mid <= keyframes[k + 1]['time']:
                a, b = keyframes[k], keyframes[k + 1]
                break
        span = b['time'] - a['time']
        t = 0.0 if span <= 0 else (mid - a['time']) / span
        color = pv.Vec3(lerp(a['color'].x, b['color'].x, t), lerp(a['color'].y, b['color'].y, t), lerp(a['color'].z, b['color'].z, t))
        new_map.append([[t0, t0 + step], color, [lerp(a['d_min'], b['d_min'], t), lerp(a['d_max'], b['d_max'], t)],
                        lerp(a['trans'], b['trans'], t)])
    return new_map


# [[temp_min, temp_max], colour, [density_min, density_max], transparency], same table as fire.py
temp_density_color_map = [
    [[0, 1],      pv.Vec3(1, 1, 1),         [0, 0.01],    0.00 * max_transparency],   # Clear open air / white smoke
    [[1, 7.5],    pv.Vec3(.1, .1, .1),      [0.01, 0.1],  0.15 * max_transparency],   # Dark grey warm smoke
    [[7.5, 15],   pv.Vec3(0.5, 0, 0),       [0.1, 0.2],   0.30 * max_transparency],   # Dark red embers
    [[15, 22.5],  pv.Vec3(0.9, 0.2, 0.05),  [0.2, 0.5],   0.55 * max_transparency],   # Vivid red flame
    [[22.5, 30],  pv.Vec3(1.0, 0.6, 0.05),  [0.5, 0.75],  0.80 * max_transparency],   # Orange flame
    [[30, 37.5],  pv.Vec3(1.0, 0.9, 0.2),   [0.75, 1.36], 0.95 * max_transparency],   # Yellow flame
    [[37.5, 46],  pv.Vec3(1.0, 1.0, 1.0),   [0.75, 1.36], 1.0 * max_transparency],    # White-hot (front logo layer)
]

# Two independent STEP inputs: temperature -> RGB, density -> alpha, packed into COLOR_RGBA
entries = [pv.LookupTableEntry([(row[0][0], row[0][1]), (row[2][0], row[2][1])], [row[1], row[3]])
           for row in expand_fire_gradient(temp_density_color_map, 96)]
mod = pv.LookupTableConverter([pv.DefaultAttributes.TEMPERATURE, pv.DefaultAttributes.DENSITY],
                              [pv.DefaultAttributes.COLOR_RGBA], entries, pv.InterpolationMode.STEP)
root = pv.AttributeModifier(mod, block)
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

if animate:
    settings = {
        "quality": "high",
        "render_mode": "volumetric",
        "visualized_attribute": "color_rgba",
        "show_bbox": False,
        "show_origin": False,
        "background_color": (1.0, 1.0, 1.0),
        "transparent_background": True,
    }
    viz.Render_Sweep_Animation(vcad_object=root, materials=pv.default_materials, output_dir="sweep_animation",
                               axis="z", duration=5.0, fps=10, loop=True, pause_seconds=0, settings=settings,
                               output_format="all", keep_frames=False)
    viz.Render_Turntable_Animation(vcad_object=root, materials=pv.default_materials, output_dir="turntable_animation",
                                   duration=5.0, fps=20, distance_multiplier=2.0, elevation_angle_deg=25.0,
                                   settings=settings, output_format="all", keep_frames=False)
