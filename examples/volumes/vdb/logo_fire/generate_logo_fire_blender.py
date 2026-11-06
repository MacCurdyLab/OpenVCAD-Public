"""
Bake the "OpenVCAD logo on fire" smoke/fire simulation with Blender Mantaflow (tested on Blender 5.0.1).

This builds the whole scene from scratch in a headless Blender: the logo mesh stands upright
facing the viewer (Blender front view, looking along +Y), and emits fuel, heat and smoke from its
volume and surface into a tall gas domain. The emitted gas starts with a small velocity away from
the viewer and upward (--velocity), so the flames and smoke stream up behind the V instead of
wrapping over its front face; that is what keeps the logo readable. The bake is written as an
OpenVDB cache: data/fluid_data_####.vdb (density, flame, temperature/heat, velocity) and, with
noise upres, noise/fluid_noise_####.vdb (density and flame at --noise times the resolution).

Pipeline (run from this folder; Blender = /Applications/Blender.app/Contents/MacOS/Blender):

    # 1. Logo mesh (repo .venv): Y up, front toward +Z, mm
    python export_logo_mesh.py logo_v.stl 0.5

    # 2. Bake (about 40 min at the defaults on a 10-core Mac; res 160 / --noise 0 takes ~3 min for previews)
    OMP_NUM_THREADS=6 Blender -b -t 6 --factory-startup --python generate_logo_fire_blender.py -- \
        --mesh logo_v.stl --cache bake

    # 3. Package one frame into logo_fire.vdb (density + temperature, fire.vdb layout)
    Blender -b --factory-startup --python package_logo_fire_vdb.py -- --cache bake --frame 115 --out logo_fire.vdb

The defaults are the settings used for the shipped logo_fire.vdb; every knob is a flag (see
--help after the "--"). Units: the logo is scaled from mm to Blender metres with --logo-scale
(0.0125 makes the 64 mm logo 0.8 m wide, a campfire-sized flame, which is what Mantaflow's
default buoyancy and burning rates are tuned for).
"""
import argparse
import json
import math
import os
import sys
import time

import bpy


def parse_args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    p = argparse.ArgumentParser(prog="generate_logo_fire_blender.py")
    p.add_argument("--mesh", required=True, help="Logo STL (Y up, front +Z, mm)")
    p.add_argument("--cache", required=True, help="Bake cache directory")
    p.add_argument("--blend", default="", help="Optionally save the scene to this .blend")
    p.add_argument("--res", type=int, default=256, help="Domain resolution along its longest (vertical) axis")
    p.add_argument("--noise", type=int, default=2, help="Noise upres factor (0 = off)")
    p.add_argument("--noise-strength", type=float, default=1.0)
    p.add_argument("--noise-scale", type=float, default=2.0, help="Noise position scale")
    p.add_argument("--frames", type=int, default=130)
    p.add_argument("--logo-scale", type=float, default=0.0125, help="Metres per mm of logo")
    p.add_argument("--domain", type=float, nargs=3, default=(1.5, 0.9, 3.0), help="Domain size x y z (m)")
    p.add_argument("--logo-base", type=float, default=0.12, help="Height of the logo's bottom above the domain floor (m)")
    p.add_argument("--vorticity", type=float, default=0.5)
    p.add_argument("--alpha", type=float, default=0.2, help="Buoyancy from smoke density (negative makes heavy smoke sink)")
    p.add_argument("--beta", type=float, default=1.0, help="Heat buoyancy")
    p.add_argument("--burning-rate", type=float, default=1.0)
    p.add_argument("--flame-smoke", type=float, default=2.0)
    p.add_argument("--flame-vorticity", type=float, default=1.0)
    p.add_argument("--flame-max-temp", type=float, default=3.0)
    p.add_argument("--flame-ignition", type=float, default=1.25)
    p.add_argument("--dissolve", type=int, default=60, help="Smoke dissolve speed in frames (0 = no dissolve)")
    p.add_argument("--fuel", type=float, default=1.0)
    p.add_argument("--temperature", type=float, default=1.5, help="Flow temperature difference")
    p.add_argument("--density", type=float, default=0.6, help="Flow smoke density")
    p.add_argument("--surface-distance", type=float, default=1.0, help="Emission distance from the surface (cells)")
    p.add_argument("--volume-density", type=float, default=1.0, help="Emission inside the volume (0-1)")
    p.add_argument("--texture", type=float, default=1.0, help="Flicker: noise texture size on the flow (0 = off)")
    p.add_argument("--velocity", type=float, nargs=3, default=(0.0, 1.0, 0.3),
                   help="Initial velocity of emitted gas (m/s, Blender axes; +Y pushes it away from the viewer)")
    p.add_argument("--velocity-normal", type=float, default=0.0, help="Initial velocity along the surface normal")
    p.add_argument("--open-sides", action="store_true", help="Let smoke leave through the side walls too (only the floor is closed)")
    p.add_argument("--subframes", type=int, default=1)
    p.add_argument("--timesteps-max", type=int, default=4)
    p.add_argument("--time-scale", type=float, default=1.0)
    return p.parse_args(argv)


def import_logo(args):
    bpy.ops.wm.stl_import(filepath=os.path.abspath(args.mesh))
    logo = bpy.context.selected_objects[0]
    logo.name = "Logo"
    # Logo frame (Y up, front +Z) -> Blender (Z up, front toward the -Y front-view camera)
    logo.rotation_euler = (math.radians(90.0), 0.0, 0.0)
    logo.scale = (args.logo_scale,) * 3
    bpy.context.view_layer.update()
    xs = [(logo.matrix_world @ v.co) for v in logo.data.vertices]
    lo = [min(p[i] for p in xs) for i in range(3)]
    hi = [max(p[i] for p in xs) for i in range(3)]
    logo.location = (-(lo[0] + hi[0]) / 2.0, -(lo[1] + hi[1]) / 2.0, args.logo_base - lo[2])
    bpy.context.view_layer.update()
    print(f"[logo] world size {hi[0]-lo[0]:.3f} x {hi[1]-lo[1]:.3f} x {hi[2]-lo[2]:.3f} m")
    return logo


def add_flow(logo, args):
    mod = logo.modifiers.new("Fluid", "FLUID")
    mod.fluid_type = "FLOW"
    flow = mod.flow_settings
    flow.flow_type = "BOTH"
    flow.flow_behavior = "INFLOW"
    flow.flow_source = "MESH"
    flow.use_plane_init = False
    flow.surface_distance = args.surface_distance
    flow.volume_density = args.volume_density
    flow.fuel_amount = args.fuel
    flow.temperature = args.temperature
    flow.density = args.density
    flow.smoke_color = (0.7, 0.7, 0.7)
    flow.subframes = args.subframes
    if any(args.velocity) or args.velocity_normal:
        flow.use_initial_velocity = True
        flow.velocity_coord = args.velocity
        flow.velocity_normal = args.velocity_normal
    if args.texture > 0.0:
        tex = bpy.data.textures.new("Flicker", type="CLOUDS")
        tex.noise_scale = 0.25
        tex.noise_depth = 2
        flow.use_texture = True
        flow.noise_texture = tex
        flow.texture_map_type = "AUTO"
        flow.texture_size = args.texture
        # Scroll the texture so the emission flickers instead of being a frozen mask
        flow.texture_offset = 0.0
        flow.keyframe_insert("texture_offset", frame=1)
        flow.texture_offset = 0.05 * args.frames
        flow.keyframe_insert("texture_offset", frame=args.frames)
        fc = logo.animation_data.action.fcurves if logo.animation_data and logo.animation_data.action and hasattr(logo.animation_data.action, "fcurves") else []
        for c in fc:
            for k in c.keyframe_points:
                k.interpolation = "LINEAR"


def add_domain(args):
    sx, sy, sz = args.domain
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.0, sz / 2.0))
    dom = bpy.context.active_object
    dom.name = "Domain"
    dom.scale = (sx, sy, sz)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    mod = dom.modifiers.new("Fluid", "FLUID")
    mod.fluid_type = "DOMAIN"
    d = mod.domain_settings
    d.domain_type = "GAS"
    d.resolution_max = args.res
    d.use_adaptive_domain = False
    d.cache_directory = os.path.abspath(args.cache)
    d.cache_type = "ALL"
    d.cache_data_format = "OPENVDB"
    d.cache_noise_format = "OPENVDB"
    d.openvdb_cache_compress_type = "ZIP"
    d.cache_frame_start = 1
    d.cache_frame_end = args.frames
    d.alpha = args.alpha
    d.beta = args.beta
    d.vorticity = args.vorticity
    d.burning_rate = args.burning_rate
    d.flame_smoke = args.flame_smoke
    d.flame_vorticity = args.flame_vorticity
    d.flame_max_temp = args.flame_max_temp
    d.flame_ignition = args.flame_ignition
    d.flame_smoke_color = (0.7, 0.7, 0.7)
    d.use_dissolve_smoke = args.dissolve > 0
    if args.dissolve > 0:
        d.dissolve_speed = args.dissolve
        d.use_dissolve_smoke_log = True
    d.timesteps_max = args.timesteps_max
    d.time_scale = args.time_scale
    d.use_collision_border_top = False   # let smoke leave through the ceiling
    if args.open_sides:
        d.use_collision_border_front = False
        d.use_collision_border_back = False
        d.use_collision_border_left = False
        d.use_collision_border_right = False
    d.use_noise = args.noise > 0
    if args.noise > 0:
        d.noise_scale = args.noise
        d.noise_strength = args.noise_strength
        d.noise_pos_scale = args.noise_scale
    return dom


def main():
    args = parse_args()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.frame_start = 1
    scene.frame_end = args.frames
    logo = import_logo(args)
    add_flow(logo, args)
    dom = add_domain(args)
    os.makedirs(args.cache, exist_ok=True)
    # Record where the logo sits relative to the domain so later steps can overlay or re-sample it
    sx, sy, sz = args.domain
    info = {"logo_location": list(logo.location), "logo_rotation_x_deg": 90.0, "logo_scale": args.logo_scale,
            "domain_min": [-sx / 2.0, -sy / 2.0, 0.0], "domain_size": [sx, sy, sz], "args": vars(args)}
    with open(os.path.join(args.cache, "scene.json"), "w") as f:
        json.dump(info, f, indent=2)
    if args.blend:
        bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(args.blend))
    print(f"[bake] res {args.res} noise {args.noise} frames {args.frames} -> {args.cache}", flush=True)
    t0 = time.time()
    with bpy.context.temp_override(scene=scene, object=dom, active_object=dom,
                                   selected_objects=[dom], view_layer=bpy.context.view_layer):
        bpy.ops.fluid.bake_all()
    print(f"[bake] done in {time.time() - t0:.1f} s", flush=True)


main()
