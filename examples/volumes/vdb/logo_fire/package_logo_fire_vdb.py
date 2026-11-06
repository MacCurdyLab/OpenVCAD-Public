"""
Package one frame of the Mantaflow logo-fire bake into logo_fire.vdb.

Run with Blender's Python (it ships the openvdb module) after
generate_logo_fire_blender.py has baked the cache:

    /Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup \
        --python package_logo_fire_vdb.py -- \
        --cache bake --frame 115 --out logo_fire.vdb

The output carries exactly two float grids, laid out like examples/volumes/vdb/fire/fire.vdb
so the fire.py two-input lookup table works unchanged:

- ``temperature``: 0 to 46. The emitter's flame (0..1) maps through a gamma onto
  0..``--flame-temp``, and hot smoke picks up a small 0..``--smoke-temp`` term from
  Mantaflow's heat grid (the dark-grey band of the LUT). Inside the logo the value is
  replaced by the ember temperature of each layer, front layer hottest, so the V reads
  as a glowing ember with flames and smoke rising off it.
- ``density``: 0 to 1.36. Mantaflow smoke density times ``--density-scale``, with the
  logo layers set to the ember densities (nearly opaque).

Axes follow fire.vdb (Houdini style): +Y is up, the viewer looks along -Z at the front of
the logo, X is left to right. Units are millimetres: the grid is scaled so that the
cropped block is ``--height-mm`` tall, and it is centred on X and Z with its base at Y=0.

The logo layers are evaluated with a numpy port of the ribbon SDF in
examples/logo/openvcad_logo.py; keep the constants below in sync with that file.
"""
import argparse
import json
import math
import os
import sys

import numpy as np
import openvdb as vdb

# ---- Logo constants, mirrored from examples/logo/openvcad_logo.py ------------------------
tip_y = 30.0
bottom_y = -22.0
half_span = 27.0
fillet_radius = 6.0
arm_radius = 140.0
ribbon_width = 10.0
ribbon_thickness = 3.0
corner_radius = 1.2
layers = 5
layer_spacing = 2.9
layer_lift = 6.5
layer_inset = 2.6


def ribbon_sdf(x, y, z, span, bottom, z_offset):
    """numpy version of v_ribbon(): signed distance (mm) to one V layer of the logo."""
    hw = ribbon_width / 2.0 - corner_radius
    hh = ribbon_thickness / 2.0 - corner_radius
    T = (span, tip_y)
    C = (0.0, bottom + fillet_radius)
    B = (0.0, bottom)
    dist = arm_radius - fillet_radius
    ex, ey = T[0] - C[0], T[1] - C[1]
    d = math.hypot(ex, ey)
    along = (dist * dist - arm_radius * arm_radius + d * d) / (2.0 * d)
    across = math.sqrt(max(dist * dist - along * along, 0.0))
    mx, my = C[0] + along * ex / d, C[1] + along * ey / d
    Ca = min(((mx - across * ey / d, my + across * ex / d), (mx + across * ey / d, my - across * ex / d)), key=lambda p: p[0])
    gx, gy = C[0] - Ca[0], C[1] - Ca[1]
    g = math.hypot(gx, gy)
    P = (Ca[0] + arm_radius * gx / g, Ca[1] + arm_radius * gy / g)
    vT = (T[0] - Ca[0], T[1] - Ca[1])
    vP_arm = (P[0] - Ca[0], P[1] - Ca[1])
    cross_arm = vT[0] * vP_arm[1] - vT[1] * vP_arm[0]
    arm_length = arm_radius * abs(math.atan2(cross_arm, vT[0] * vP_arm[0] + vT[1] * vP_arm[1]))
    vP = (P[0] - C[0], P[1] - C[1])
    vB = (B[0] - C[0], B[1] - C[1])
    cross_fillet = vP[0] * vB[1] - vP[1] * vB[0]

    xa = np.abs(x)
    zz = z - z_offset

    def arc(cx, cy, radius, ref, direction, s0):
        dx = xa - cx
        dy = y - cy
        c = radius - np.sqrt(dx * dx + dy * dy)
        s = s0 + radius * direction * np.arctan2(ref[0] * dy - ref[1] * dx, ref[0] * dx + ref[1] * dy)
        return c, s

    def piece(c, cap):
        qx = np.abs(c) - hw
        qz = np.abs(zz) - hh
        qy = cap
        outside = np.sqrt(np.maximum(qx, 0) ** 2 + np.maximum(qy, 0) ** 2 + np.maximum(qz, 0) ** 2)
        return outside + np.minimum(np.maximum(qx, np.maximum(qy, qz)), 0) - corner_radius

    ca, sa = arc(Ca[0], Ca[1], arm_radius, vT, 1.0 if cross_arm > 0 else -1.0, 0.0)
    cf, sf = arc(C[0], C[1], fillet_radius, vP, 1.0 if cross_fillet > 0 else -1.0, arm_length)
    return np.minimum(piece(ca, np.maximum(-sa, sa - arm_length)), piece(cf, arm_length - sf))


def layer_sdf(i, x, y, z):
    return ribbon_sdf(x, y, z, half_span - i * layer_inset, bottom_y + i * layer_lift, -i * layer_spacing)


# ---- Helpers -----------------------------------------------------------------------------
def parse_args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    p = argparse.ArgumentParser(prog="package_logo_fire_vdb.py")
    p.add_argument("--cache", required=True)
    p.add_argument("--frame", type=int, required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--height-mm", type=float, default=100.0, help="Height of the cropped block in mm")
    p.add_argument("--height-voxels", type=int, default=400, help="Output voxels along the height")
    p.add_argument("--crop-density", type=float, default=0.01, help="Crop X/Z to where density exceeds this")
    p.add_argument("--crop-margin", type=float, default=0.04, help="Crop margin as a fraction of the height")
    p.add_argument("--top", type=float, default=1.0, help="Keep this fraction of the domain height")
    p.add_argument("--flame-temp", type=float, default=32.0, help="Temperature of full flame (yellow-orange)")
    p.add_argument("--flame-gamma", type=float, default=0.8)
    p.add_argument("--smoke-temp", type=float, default=2.5, help="Temperature added to hot smoke (grey band)")
    p.add_argument("--density-scale", type=float, default=1.15)
    p.add_argument("--density-floor", type=float, default=0.2,
                   help="Smoke density below this prints clear; the plume fades in over the next floor-width")
    p.add_argument("--ember-temp", default="44,34,26,18,10", help="Ember temperature per layer, front to back")
    p.add_argument("--ember-density", default="1.3,1.25,1.2,1.15,1.1", help="Ember density per layer")
    p.add_argument("--ember-halo-mm", type=float, default=1.5, help="Logo-mm glow falloff around each layer")
    p.add_argument("--front-clear", type=float, default=1.0,
                   help="0..1: how much smoke density to remove in front of the logo, so the ember stays visible")
    p.add_argument("--front-clear-flame", type=float, default=1.0,
                   help="0..1: the same for flame, lower keeps flame tongues licking over the V's face")
    p.add_argument("--ember-crackle", type=float, default=0.25,
                   help="0..1: mottle the ember glow with smooth noise so it reads as burning embers, not flat bands")
    p.add_argument("--crackle-mm", type=float, default=2.0, help="Logo-mm size of the crackle pattern")
    p.add_argument("--no-ember", action="store_true")
    p.add_argument("--wall-feather-mm", type=float, default=5.0,
                   help="Fade smoke and flame smoothly to zero over this many print mm at all six faces, so "
                        "nothing is cut flat where the plume reached the simulation domain walls")
    p.add_argument("--tolerance", type=float, default=2e-4, help="Values below this become inactive")
    p.add_argument("--dump-npz", default="", help="Also save the output arrays (Y-up) to this .npz")
    return p.parse_args(argv)


def read_grids(path, names):
    """Dense arrays of the named grids over the whole cache grid, plus its (cubic) voxel size."""
    out = {}
    for g in vdb.readAll(path)[0]:
        if g.name in names:
            res = tuple(int(v) for v in g["file_base_resolution"])
            a = np.zeros(res, dtype=np.float32)
            g.copyToArray(a, ijk=(0, 0, 0))
            out[g.name] = a
            out["voxel"] = float(g.transform.voxelSize()[0])
    return out


def resample(a, new_shape):
    """Separable linear resampling of a cell-centred grid to new_shape (same physical extent)."""
    for axis, n in enumerate(new_shape):
        m = a.shape[axis]
        if m == n:
            continue
        pos = np.clip((np.arange(n) + 0.5) * m / n - 0.5, 0, m - 1)
        i0 = np.floor(pos).astype(np.int64)
        i1 = np.minimum(i0 + 1, m - 1)
        w = (pos - i0).astype(np.float32)
        shape = [1, 1, 1]
        shape[axis] = n
        w = w.reshape(shape)
        a = np.take(a, i0, axis=axis) * (1 - w) + np.take(a, i1, axis=axis) * w
    return a.astype(np.float32)


def main():
    args = parse_args()
    info = json.load(open(os.path.join(args.cache, "scene.json")))
    f = f"{args.frame:04d}"
    data = read_grids(os.path.join(args.cache, "data", f"fluid_data_{f}.vdb"), ("density", "flame", "temperature"))
    heat = data["temperature"]
    h = data["voxel"]
    noise_path = os.path.join(args.cache, "noise", f"fluid_noise_{f}.vdb")
    if os.path.exists(noise_path):
        hi = read_grids(noise_path, ("density_noise", "flame_noise"))
        density, flame = hi["density_noise"], hi["flame_noise"]
        heat = resample(heat, density.shape)
        h = hi["voxel"]
        print(f"[package] noise grids {density.shape}, base {data['density'].shape}")
    else:
        density, flame = data["density"], data["flame"]
        print(f"[package] base grids {density.shape} (no noise cache)")

    # Remap to fire.vdb's ranges
    fl = np.clip(flame / max(float(flame.max()), 1e-6), 0.0, 1.0)
    temperature = args.flame_temp * fl ** args.flame_gamma + args.smoke_temp * np.clip(heat / 3.0, 0, 1) ** 2 * (1 - fl)
    # Thin haze -> clear: a smooth ramp from floor to 2*floor so the plume keeps soft but definite edges
    if args.density_floor > 0.0:
        ramp = np.clip((density - args.density_floor) / args.density_floor, 0.0, 1.0)
        density = density * ramp * ramp * (3.0 - 2.0 * ramp)
    density = np.clip(density * args.density_scale, 0.0, 1.36)
    del flame, fl, heat

    # Physical frame of the cache (Blender metres, Z up)
    dmin = np.array(info["domain_min"])
    n = np.array(density.shape)
    cell = np.array([h, h, h])                     # cell (0, 0, 0) starts at the domain's min corner

    # Crop: full width where smoke reaches, from the floor up to --top of the domain
    keep_z = int(round(n[2] * args.top))
    occ = density[:, :, :keep_z] > args.crop_density
    margin = int(round(args.crop_margin * keep_z))
    xs = np.where(occ.any(axis=(1, 2)))[0]
    ys = np.where(occ.any(axis=(0, 2)))[0]
    if xs.size == 0:                              # nothing above the threshold: keep the whole domain
        xs, ys = np.array([0, n[0] - 1]), np.array([0, n[1] - 1])
    x0, x1 = max(xs[0] - margin, 0), min(xs[-1] + margin + 1, n[0])
    y0, y1 = max(ys[0] - margin, 0), min(ys[-1] + margin + 1, n[1])
    density = density[x0:x1, y0:y1, :keep_z]
    temperature = temperature[x0:x1, y0:y1, :keep_z]
    crop_min = dmin + np.array([x0, y0, 0]) * cell
    crop_size = np.array(density.shape) * cell
    print(f"[package] crop cells x {x0}:{x1} y {y0}:{y1} z 0:{keep_z} -> {crop_size.round(3)} m")

    # Resample to the output resolution (cubic voxels)
    vox_m = crop_size[2] / args.height_voxels
    out_shape = tuple(int(round(s / vox_m)) for s in crop_size)
    density = resample(density, out_shape)
    temperature = resample(temperature, out_shape)
    vox_m = crop_size / np.array(out_shape)

    # Wall feather: smoothstep from 0 at each face to 1 at --wall-feather-mm inside it (before the ember,
    # so the logo itself is never faded)
    if args.wall_feather_mm > 0.0:
        band = args.wall_feather_mm / (args.height_mm / out_shape[2])   # in output voxels
        for axis, n_axis in enumerate(out_shape):
            t = np.clip(np.minimum(np.arange(n_axis) + 0.5, n_axis - 0.5 - np.arange(n_axis)) / band, 0.0, 1.0)
            ramp = (t * t * (3.0 - 2.0 * t)).astype(np.float32)
            shape = [1, 1, 1]
            shape[axis] = n_axis
            density *= ramp.reshape(shape)
            temperature *= ramp.reshape(shape)

    # Ember: the logo layers glow, front layer hottest
    if not args.no_ember:
        s = info["logo_scale"]
        L = np.array(info["logo_location"])
        X = crop_min[0] + (np.arange(out_shape[0]) + 0.5) * vox_m[0]
        Y = crop_min[1] + (np.arange(out_shape[1]) + 0.5) * vox_m[1]
        Z = crop_min[2] + (np.arange(out_shape[2]) + 0.5) * vox_m[2]
        # Blender world -> logo mm: x = (X-Lx)/s, y = (Z-Lz)/s, z = -(Y-Ly)/s
        xl, zl, yl = (X - L[0]) / s, -(Y - L[1]) / s, (Z - L[2]) / s
        pad = 4.0 + args.ember_halo_mm
        ix = np.where(np.abs(xl) < half_span + ribbon_width + pad)[0]
        iy = np.where(zl > -(layers - 1) * layer_spacing - ribbon_thickness - pad)[0]   # from the block's front face back
        iz = np.where((yl > bottom_y - pad) & (yl < tip_y + ribbon_width + pad))[0]
        sl = (slice(ix[0], ix[-1] + 1), slice(iy[0], iy[-1] + 1), slice(iz[0], iz[-1] + 1))
        # Arrays are (x, depth, up); gy holds logo y (up) and gz logo z (depth)
        gx, gz, gy = np.meshgrid(xl[sl[0]], zl[sl[1]], yl[sl[2]], indexing="ij")
        vmm = float(vox_m[2] / s)
        Ts, Ds = temperature[sl], density[sl]
        ember_t = [float(v) for v in args.ember_temp.split(",")]
        ember_d = [float(v) for v in args.ember_density.split(",")]
        sdfs = [layer_sdf(i, gx, gy, gz).astype(np.float32) for i in range(layers)]
        if args.front_clear > 0.0:
            # Viewing window: thin out the gas between the viewer (+logo z, which is the -Y side of
            # the cache) and the front-most logo surface, inside the logo's front footprint
            solid = np.min(sdfs, axis=0) <= 0.0                       # (x, depth, up), depth index runs front -> back
            seen = solid.any(axis=1)                                  # (x, up) front footprint
            front = np.where(seen, np.argmax(solid, axis=1), -1)
            # Inside the V's notch (between the outer edges of each row) clear through to the back layer
            back = int(np.searchsorted(-gz[0, :, 0], (layers - 1) * layer_spacing + ribbon_thickness / 2.0))
            cols = np.arange(seen.shape[0])[:, None]
            has = seen.any(axis=0)
            left = np.where(has, np.argmax(seen, axis=0), seen.shape[0])
            right = np.where(has, seen.shape[0] - 1 - np.argmax(seen[::-1], axis=0), -1)
            notch = (cols >= left[None, :]) & (cols <= right[None, :]) & ~seen
            front = np.where(notch, back, front)
            window = (np.arange(solid.shape[1])[None, :, None] < front[:, None, :]).astype(np.float32)
            for axis in (0, 2):                                       # feather the footprint edge
                window = (np.roll(window, 1, axis) + window + np.roll(window, -1, axis)) / 3.0
            flame_part = np.clip(Ts / max(args.flame_temp, 1e-6), 0.0, 1.0)
            Ds *= 1.0 - window * (args.front_clear * (1.0 - flame_part) + args.front_clear_flame * flame_part)
        # Smooth value noise in [0, 1] over the ember region (fixed seed, so packaging is reproducible)
        crackle = np.zeros(gx.shape, np.float32)
        if args.ember_crackle > 0.0:
            coarse = tuple(max(int(np.ceil(n_ * vmm / args.crackle_mm)) + 1, 2) for n_ in gx.shape)
            crackle = resample(np.random.default_rng(7).random(coarse).astype(np.float32), gx.shape)
            crackle = (crackle - crackle.min()) / max(float(crackle.max() - crackle.min()), 1e-6)
        for i in range(layers - 1, -1, -1):           # back to front, so the front layer wins
            d = sdfs[i]
            t_i = ember_t[i] * (1.0 - args.ember_crackle * crackle)
            cover = np.clip(0.5 - d / vmm, 0.0, 1.0)
            glow = np.clip(1.0 - d / max(args.ember_halo_mm, 1e-6), 0.0, 1.0) * (d > 0)
            Ts[:] = np.maximum(Ts, 0.85 * t_i * glow)
            Ts[:] = Ts * (1 - cover) + t_i * cover
            Ds[:] = Ds * (1 - cover) + ember_d[i] * cover
            print(f"[package] ember layer {i}: {int((d <= 0).sum())} voxels inside, T {ember_t[i]}")

    # Blender (x, y depth, z up) -> fire.vdb layout (x, y up, z toward the viewer): z_out = -y
    density = np.ascontiguousarray(np.transpose(density, (0, 2, 1))[:, :, ::-1])
    temperature = np.ascontiguousarray(np.transpose(temperature, (0, 2, 1))[:, :, ::-1])
    density[density < args.tolerance] = 0.0
    temperature[temperature < args.tolerance] = 0.0

    mm = vox_m * 1000.0 * (args.height_mm / (crop_size[2] * 1000.0))
    v = float(mm[2])
    nx, ny, nz = density.shape
    origin = (-0.5 * nx * v + 0.5 * v, 0.5 * v, -0.5 * nz * v + 0.5 * v)   # voxel centres; centred on X/Z, base at Y=0
    xform = [[v, 0, 0, 0], [0, v, 0, 0], [0, 0, v, 0], [origin[0], origin[1], origin[2], 1]]
    grids = []
    for name, arr in (("density", density), ("temperature", temperature)):
        g = vdb.FloatGrid(0.0)
        g.name = name
        g.gridClass = vdb.GridClass.FOG_VOLUME
        g.copyFromArray(arr, ijk=(0, 0, 0), tolerance=0.0)
        g.transform = vdb.createLinearTransform(xform)
        g.saveFloatAsHalf = True
        g.pruneInactive()
        grids.append(g)
        nzv = arr[arr > 0]
        print(f"[package] {name}: shape {arr.shape} min {arr.min():.4g} max {arr.max():.4g} active {g.activeVoxelCount()} "
              f"p50/p90/p99 of active {np.percentile(nzv, [50, 90, 99]).round(3).tolist()}")
    meta = {"creator": "OpenVCAD generate_logo_fire_blender.py + package_logo_fire_vdb.py (Blender Mantaflow)",
            "source_frame": str(args.frame), "voxel_size_mm": f"{v:.5f}",
            "ranges": "temperature 0..46 (flame + ember), density 0..1.36",
            "package_args": json.dumps({k: val for k, val in vars(args).items() if k not in ("cache", "out", "dump_npz")}),
            "sim_args": json.dumps(info.get("args", {}))}
    vdb.write(args.out, grids=grids, metadata=meta)
    print(f"[package] wrote {args.out} ({os.path.getsize(args.out) / 1e6:.1f} MB), {nx}x{ny}x{nz} voxels of {v:.4f} mm "
          f"-> {nx * v:.1f} x {ny * v:.1f} x {nz * v:.1f} mm")
    if args.dump_npz:
        np.savez_compressed(args.dump_npz, density=density, temperature=temperature,
                            voxel_size=np.array([v, v, v]), origin_ijk=np.array([0, 0, 0]),
                            density_active=np.int64(grids[0].activeVoxelCount()),
                            temperature_active=np.int64(grids[1].activeVoxelCount()))


main()
